"""
Storage Manager - Handles local filesystem and S3 storage for screenshots and reports
"""
import os
import gzip
import bz2
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def save_file(self, file_path: str, content: bytes) -> str:
        """Save file and return the storage path."""
        pass

    @abstractmethod
    def get_file(self, storage_path: str) -> bytes:
        """Retrieve file content from storage."""
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    def list_files(self, prefix: str) -> list:
        """List files with given prefix."""
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self, base_path: str = "/app/screenshots"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_file(self, file_path: str, content: bytes) -> str:
        """Save file to local filesystem."""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'wb') as f:
            f.write(content)

        return str(full_path)

    def get_file(self, storage_path: str) -> bytes:
        """Retrieve file from local filesystem."""
        with open(storage_path, 'rb') as f:
            return f.read()

    def delete_file(self, storage_path: str) -> bool:
        """Delete file from local filesystem."""
        try:
            Path(storage_path).unlink()
            return True
        except FileNotFoundError:
            return False

    def list_files(self, prefix: str) -> list:
        """List files with given prefix."""
        prefix_path = self.base_path / prefix
        if not prefix_path.exists():
            return []
        return [str(p) for p in prefix_path.glob("*")]


class S3StorageBackend(StorageBackend):
    """Amazon S3 storage backend."""

    def __init__(self, bucket: str, region: str = "us-east-1", 
                 access_key: Optional[str] = None, secret_key: Optional[str] = None):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
        except ImportError:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")

        self.bucket = bucket
        self.region = region

    def save_file(self, file_path: str, content: bytes) -> str:
        """Save file to S3."""
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=file_path,
            Body=content
        )
        return f"s3://{self.bucket}/{file_path}"

    def get_file(self, storage_path: str) -> bytes:
        """Retrieve file from S3."""
        response = self.s3_client.get_object(Bucket=self.bucket, Key=storage_path)
        return response['Body'].read()

    def delete_file(self, storage_path: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=storage_path)
            return True
        except Exception:
            return False

    def list_files(self, prefix: str) -> list:
        """List files with given prefix in S3."""
        response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]

    def get_presigned_url(self, file_path: str, expiration: int = 3600) -> str:
        """Get presigned URL for file access."""
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': file_path},
            ExpiresIn=expiration
        )


class StorageManager:
    """Manager for handling file storage with multiple backends."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backend = self._initialize_backend()
        self.compression = config.get('storage', {}).get('compression', 'none')

    def _initialize_backend(self) -> StorageBackend:
        """Initialize appropriate storage backend based on config."""
        storage_type = self.config.get('storage', {}).get('screenshot_storage', 'local')

        if storage_type == 's3':
            return S3StorageBackend(
                bucket=self.config.get('storage', {}).get('s3_bucket'),
                region=self.config.get('storage', {}).get('s3_region', 'us-east-1'),
                access_key=self.config.get('storage', {}).get('s3_access_key'),
                secret_key=self.config.get('storage', {}).get('s3_secret_key'),
            )
        else:
            return LocalStorageBackend(
                base_path=self.config.get('storage', {}).get('local_path', '/app/screenshots')
            )

    def save_screenshot(self, url: str, content: bytes, crawler_type: str, timestamp: str) -> str:
        """
        Save screenshot file.

        Args:
            url: URL of the page
            content: Screenshot image bytes
            crawler_type: Type of crawler
            timestamp: Timestamp for grouping

        Returns:
            Storage path
        """
        # Generate file name from URL
        safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_')
        file_name = f"{safe_url}_{timestamp}.png"
        file_path = f"{crawler_type}/{timestamp}/{file_name}"

        # Compress if configured
        if self.compression in ['gzip', 'bz2']:
            content = self._compress(content, self.compression)
            file_path += f".{self.compression}"

        return self.backend.save_file(file_path, content)

    def get_screenshot(self, storage_path: str) -> bytes:
        """Retrieve screenshot from storage."""
        content = self.backend.get_file(storage_path)

        # Decompress if needed
        if storage_path.endswith('.gz'):
            content = gzip.decompress(content)
        elif storage_path.endswith('.bz2'):
            content = bz2.decompress(content)

        return content

    def delete_screenshot(self, storage_path: str) -> bool:
        """Delete screenshot from storage."""
        return self.backend.delete_file(storage_path)

    def list_screenshots(self, crawler_type: str, timestamp: str = None) -> list:
        """List screenshots for given crawler type."""
        prefix = f"{crawler_type}/{timestamp}" if timestamp else crawler_type
        return self.backend.list_files(prefix)

    @staticmethod
    def _compress(data: bytes, method: str) -> bytes:
        """Compress data using specified method."""
        if method == 'gzip':
            return gzip.compress(data)
        elif method == 'bz2':
            return bz2.compress(data)
        return data
