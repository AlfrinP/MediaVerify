from fastapi import APIRouter, Depends, HTTPException, status, Request
from ..models.user import UserCreate, User, UserUpdate, UserInDB
from ..services.auth_service import get_current_active_user, get_password_hash
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

router = APIRouter()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, request: Request):
    # Check if username already exists
    if await request.app.mongodb["users"].find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email already exists
    if await request.app.mongodb["users"].find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["_id"] = str(ObjectId())

    await request.app.mongodb["users"].insert_one(user_dict)

    created_user = await request.app.mongodb["users"].find_one(
        {"_id": user_dict["_id"]}
    )
    return User(**created_user)


@router.get("/me", response_model=User)
async def read_user_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    request: Request = None,
):
    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    if update_data:
        update_result = await request.app.mongodb["users"].update_one(
            {"_id": current_user.id}, {"$set": update_data}
        )
        if update_result.modified_count == 1:
            updated_user = await request.app.mongodb["users"].find_one(
                {"_id": current_user.id}
            )
            return User(**updated_user)

    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    current_user: UserInDB = Depends(get_current_active_user), request: Request = None
):
    delete_result = await request.app.mongodb["users"].delete_one(
        {"_id": current_user.id}
    )
    if delete_result.deleted_count != 1:
        raise HTTPException(status_code=404, detail="User not found")
