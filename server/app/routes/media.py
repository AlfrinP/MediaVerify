from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from ..models.media import Media, MediaCreate, MediaUpdate, MediaStatus
from ..models.user import UserInDB
from ..services.auth_service import get_current_active_user
from ..services.storage_service import StorageService
from typing import List
from datetime import datetime
from bson import ObjectId

router = APIRouter()
storage_service = StorageService()


@router.post("/upload", response_model=Media)
async def upload_media(
    file: UploadFile = File(...),
    description: str = None,
    current_user: UserInDB = Depends(get_current_active_user),
    request: Request = None,
):
    # Upload file to S3
    s3_key, file_type, file_size, mime_type = await storage_service.upload_file(
        file, current_user.username
    )

    # Create media record
    media_data = {
        "_id": str(ObjectId()),
        "filename": file.filename,
        "file_type": file_type,
        "file_size": file_size,
        "mime_type": mime_type,
        "description": description,
        "user_id": current_user.id,
        "s3_key": s3_key,
        "status": MediaStatus.PENDING,
        "uploaded_at": datetime.utcnow(),
    }

    await request.app.mongodb["media"].insert_one(media_data)
    return Media(**media_data)


@router.get("/me", response_model=List[Media])
async def list_user_media(
    current_user: UserInDB = Depends(get_current_active_user), request: Request = None
):
    cursor = request.app.mongodb["media"].find({"user_id": current_user.id})
    media_list = await cursor.to_list(length=None)
    return [Media(**media) for media in media_list]


@router.get("/{media_id}", response_model=Media)
async def get_media(
    media_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    request: Request = None,
):
    media = await request.app.mongodb["media"].find_one(
        {"_id": media_id, "user_id": current_user.id}
    )
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # Generate presigned URL for the media file
    media["url"] = storage_service.get_file_url(media["s3_key"])
    return Media(**media)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    request: Request = None,
):
    # Find media first to get S3 key
    media = await request.app.mongodb["media"].find_one(
        {"_id": media_id, "user_id": current_user.id}
    )
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # Delete from S3
    storage_service.delete_file(media["s3_key"])

    # Delete from database
    delete_result = await request.app.mongodb["media"].delete_one(
        {"_id": media_id, "user_id": current_user.id}
    )
    if delete_result.deleted_count != 1:
        raise HTTPException(status_code=500, detail="Failed to delete media record")
