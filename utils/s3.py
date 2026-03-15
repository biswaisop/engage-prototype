import boto3
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class S3Service:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = boto3.client(
                "s3",
                region_name = os.getenv("AWS_REGION", "us_east_1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            logger.info("S3 client initialized")
        return cls._client
    
    @classmethod
    def upload(cls, file_bytes: bytes, s3_key: str, content_type: str) -> str:
        """Upload file to s3, return s3_key"""
        try:
            cls.get_client().put_object(
                Bucket = os.getenv("S3_BUCKET"),
                Key = s3_key,
                Body = file_bytes,
                ContentType = content_type
            )
            logger.info(f"[S3] Uploaded → {s3_key}")
            return s3_key
        except Exception as e:
            logger.error(f"[S3] Upload failed: {e}")
            raise
    
    @classmethod
    def download(cls, s3_key: str) -> bytes:
        """Download file from s3, return bytes"""
        try:
            response = cls.get_client().get_object(
                Bucket = os.getenv("S3_BUCKET"),
                Key = s3_key
            )
            logger.info(f"[S3] Downloaded → {s3_key}")
            return response["Body"].read()
        except Exception as e:
            logger.error(f"[S3] Download failed: {e}")
            raise
    @classmethod
    def delete(cls, s3_key: str):
        """Delete file from s3, return s3_key"""
        try:
            cls.get_client().delete_object(
                Bucket = os.getenv("S3_BUCKET"),
                Key = s3_key,
            )
            logger.info(f"[S3] Deleted → {s3_key}")
        except Exception as e:
            logger.error(f"[S3] Delete failed: {e}")
            raise

    @classmethod
    def get_url(cls, s3_key: str, expiry: int = 3600) -> str:
        """Generate presigned URL to retrieve file from s3 """
        try:
            url = cls.get_client().generate_presigned_url(
                "get_object",
                Params={"Bucket": os.getenv("S3_BUCKET"), "Key": s3_key},
                ExpiresIn=expiry,
            )
            logger.info(f"[S3] Generated URL for -> {s3_key}")
            return url
        except Exception as e:
            logger.error(f"[S3] Generate URL failed: {e}")
            raise
    