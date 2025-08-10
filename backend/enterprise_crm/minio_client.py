"""
MinIO client for file storage
"""
from minio import Minio
from minio.error import S3Error
import os
import uuid
from typing import Optional, BinaryIO, Dict
from fastapi import UploadFile
from .config import settings

class MinIOClient:
    def __init__(self):
        try:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            self.bucket_name = settings.MINIO_BUCKET
            self.available = True
            self._ensure_bucket()
            print("MinIO connection established")
        except Exception as e:
            print(f"Warning: MinIO connection failed: {e}")
            print("File storage will be disabled")
            self.client = None
            self.available = False
    
    def _ensure_bucket(self):
        """Ensure the bucket exists"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except Exception as e:
            print(f"Warning: MinIO connection failed: {e}")
            # Continue without MinIO for testing
    
    def upload_file(self, file: UploadFile, folder: str = "uploads") -> Optional[str]:
        """Upload file and return file path"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            object_name = f"{folder}/{unique_filename}"
            
            # Reset file pointer to beginning
            file.file.seek(0)
            
            # Upload file
            self.client.put_object(
                self.bucket_name,
                object_name,
                file.file,
                length=-1,  # Unknown length
                part_size=10*1024*1024,  # 10MB
                content_type=file.content_type
            )
            
            return object_name
        except S3Error as e:
            print(f"Error uploading file: {e}")
            return None
    
    def download_file(self, object_name: str) -> Optional[BinaryIO]:
        """Download file and return file object"""
        try:
            return self.client.get_object(self.bucket_name, object_name)
        except S3Error as e:
            print(f"Error downloading file: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """Delete file"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_url(self, object_name: str, expires_in_minutes: int = 60) -> Optional[str]:
        """Get presigned URL for file access"""
        try:
            from datetime import timedelta
            return self.client.presigned_get_object(
                self.bucket_name, 
                object_name,
                expires=timedelta(minutes=expires_in_minutes)
            )
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def list_files(self, prefix: str = "") -> list:
        """List files in bucket with optional prefix"""
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Error listing files: {e}")
            return []

# Global MinIO client instance
minio_client = MinIOClient()