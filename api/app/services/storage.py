"""Cloudflare R2 Storage Service (S3-compatible)"""

import boto3
from botocore.config import Config
from typing import BinaryIO, Optional
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


class R2StorageService:
    """Service for interacting with Cloudflare R2 storage."""

    def __init__(self):
        settings = get_settings()

        if not settings.r2_endpoint:
            self._client = None
            logger.warning("R2 storage not configured - missing endpoint")
            return

        self._client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        )
        self._bucket = settings.r2_bucket_name

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload a file to R2.

        Args:
            file: File-like object to upload
            key: Object key (path) in the bucket
            content_type: Optional MIME type

        Returns:
            The object key
        """
        if not self.is_configured:
            raise RuntimeError("R2 storage not configured")

        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        self._client.upload_fileobj(file, self._bucket, key, ExtraArgs=extra_args)
        logger.info(f"Uploaded file to R2: {key}")
        return key

    def download_file(self, key: str) -> bytes:
        """
        Download a file from R2.

        Args:
            key: Object key (path) in the bucket

        Returns:
            File contents as bytes
        """
        if not self.is_configured:
            raise RuntimeError("R2 storage not configured")

        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def delete_file(self, key: str) -> bool:
        """
        Delete a file from R2.

        Args:
            key: Object key (path) in the bucket

        Returns:
            True if deleted successfully
        """
        if not self.is_configured:
            raise RuntimeError("R2 storage not configured")

        self._client.delete_object(Bucket=self._bucket, Key=key)
        logger.info(f"Deleted file from R2: {key}")
        return True

    def list_files(self, prefix: str = "", max_keys: int = 1000) -> list[dict]:
        """
        List files in R2 bucket.

        Args:
            prefix: Filter by key prefix
            max_keys: Maximum number of keys to return

        Returns:
            List of object metadata dicts
        """
        if not self.is_configured:
            raise RuntimeError("R2 storage not configured")

        response = self._client.list_objects_v2(
            Bucket=self._bucket,
            Prefix=prefix,
            MaxKeys=max_keys,
        )

        return [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"],
            }
            for obj in response.get("Contents", [])
        ]

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned URL for temporary access.

        Args:
            key: Object key (path) in the bucket
            expires_in: URL expiration time in seconds

        Returns:
            Presigned URL string
        """
        if not self.is_configured:
            raise RuntimeError("R2 storage not configured")

        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )


# Singleton instance
_storage_service: Optional[R2StorageService] = None


def get_storage_service() -> R2StorageService:
    """Get or create the R2 storage service singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = R2StorageService()
    return _storage_service
