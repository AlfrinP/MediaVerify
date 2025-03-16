from fastapi import APIRouter, Depends, HTTPException, status, Request
from ..models.user import UserInDB, User, UserRole
from ..models.media import Media, MediaUpdate, MediaStatus
from ..services.auth_service import get_current_active_user
from typing import List
from datetime import datetime

router = APIRouter()


async def get_current_admin(
    current_user: UserInDB = Depends(get_current_active_user),
) -> UserInDB:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


@router.get("/users", response_model=List[User])
async def list_users(
    request: Request, current_user: UserInDB = Depends(get_current_admin)
):
    cursor = request.app.mongodb["users"].find({})
    users = await cursor.to_list(length=None)
    return [User(**user) for user in users]


@router.put("/users/{user_id}/role", response_model=User)
async def update_user_role(
    user_id: str,
    role: UserRole,
    request: Request,
    current_user: UserInDB = Depends(get_current_admin),
):
    # Prevent admin from changing their own role
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    update_result = await request.app.mongodb["users"].update_one(
        {"_id": user_id}, {"$set": {"role": role}}
    )

    if update_result.modified_count != 1:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await request.app.mongodb["users"].find_one({"_id": user_id})
    return User(**updated_user)


@router.get("/media/pending", response_model=List[Media])
async def list_pending_media(
    request: Request, current_user: UserInDB = Depends(get_current_admin)
):
    cursor = request.app.mongodb["media"].find({"status": MediaStatus.PENDING})
    media_list = await cursor.to_list(length=None)
    return [Media(**media) for media in media_list]


@router.put("/media/{media_id}/review", response_model=Media)
async def review_media(
    media_id: str,
    media_update: MediaUpdate,
    request: Request,
    current_user: UserInDB = Depends(get_current_admin),
):
    # Find media first
    media = await request.app.mongodb["media"].find_one({"_id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # Update media status
    update_data = {
        "status": media_update.status,
        "review_notes": media_update.review_notes,
        "reviewed_at": datetime.utcnow(),
        "reviewed_by": current_user.id,
    }

    update_result = await request.app.mongodb["media"].update_one(
        {"_id": media_id}, {"$set": update_data}
    )

    if update_result.modified_count != 1:
        raise HTTPException(status_code=500, detail="Failed to update media status")

    updated_media = await request.app.mongodb["media"].find_one({"_id": media_id})
    return Media(**updated_media)


@router.get("/stats")
async def get_admin_stats(
    request: Request, current_user: UserInDB = Depends(get_current_admin)
):
    total_users = await request.app.mongodb["users"].count_documents({})
    total_media = await request.app.mongodb["media"].count_documents({})
    pending_media = await request.app.mongodb["media"].count_documents(
        {"status": MediaStatus.PENDING}
    )
    approved_media = await request.app.mongodb["media"].count_documents(
        {"status": MediaStatus.APPROVED}
    )
    rejected_media = await request.app.mongodb["media"].count_documents(
        {"status": MediaStatus.REJECTED}
    )

    return {
        "total_users": total_users,
        "total_media": total_media,
        "media_stats": {
            "pending": pending_media,
            "approved": approved_media,
            "rejected": rejected_media,
        },
    }
