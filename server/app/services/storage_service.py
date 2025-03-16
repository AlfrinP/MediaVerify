import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile
import magic
from ..config.settings import settings
from ..models.media import MediaType
import uuid


class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.AWS_S3_BUCKET

    def _get_file_type(self, file: UploadFile) -> MediaType:
        mime = magic.Magic(mime=True)
        file_content = file.file.read(2048)
        file.file.seek(0)  # Reset file pointer
        mime_type = mime.from_buffer(file_content)

        if mime_type in settings.ALLOWED_IMAGE_TYPES:
            return MediaType.IMAGE
        elif mime_type in settings.ALLOWED_AUDIO_TYPES:
            return MediaType.AUDIO
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported file type: {mime_type}"
            )

    async def upload_file(
        self, file: UploadFile, username: str
    ) -> tuple[str, MediaType, int, str]:
        file_type = self._get_file_type(file)
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes",
            )

        # Generate unique S3 key
        file_extension = file.filename.split(".")[-1]
        s3_key = f"users/{username}/{file_type.value}/{uuid.uuid4()}.{file_extension}"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type,
            )
            return s3_key, file_type, file_size, file.content_type
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload file: {str(e)}"
            )

    def get_file_url(self, s3_key: str) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=3600,  # URL expires in 1 hour
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate URL: {str(e)}"
            )

    def delete_file(self, s3_key: str) -> None:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete file: {str(e)}"
            )
