"""
MinIO client for file storage
"""
from minio import Minio
from minio.error import S3Error
import os
import uuid
from typing import Optional, BinaryIO
from fastapi import UploadFile
from ..config import settings

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
            print("✅ MinIO connection established")
        except Exception as e:
            print(f"⚠️  MinIO connection failed: {e}")
            print("📁 File storage will be disabled")
            self.client = None
            self.available = False
    
    def _ensure_bucket(self):
        """Ensure the bucket exists"""
        if not self.available:
            return
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"📁 Created MinIO bucket: {self.bucket_name}")
        except Exception as e:
            print(f"⚠️  MinIO bucket creation failed: {e}")
            self.available = False
    
    def upload_file(self, file: UploadFile, folder: str = "uploads") -> Optional[str]:
        """Upload file and return file path"""
        if not self.available:
            # Mock file upload for testing
            return f"mock_uploads/{uuid.uuid4()}_{file.filename}"
        
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
            print(f"❌ File upload error: {e}")
            return None
    
    def download_file(self, object_name: str) -> Optional[BinaryIO]:
        """Download file and return file object"""
        if not self.available:
            return None
            
        try:
            return self.client.get_object(self.bucket_name, object_name)
        except S3Error as e:
            print(f"❌ File download error: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """Delete file"""
        if not self.available:
            return True  # Mock success
            
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"❌ File delete error: {e}")
            return False
    
    def get_file_url(self, object_name: str, expires_in_minutes: int = 60) -> Optional[str]:
        """Get presigned URL for file access"""
        if not self.available:
            return f"http://localhost:8000/files/mock/{object_name}"
            
        try:
            from datetime import timedelta
            return self.client.presigned_get_object(
                self.bucket_name, 
                object_name,
                expires=timedelta(minutes=expires_in_minutes)
            )
        except S3Error as e:
            print(f"❌ URL generation error: {e}")
            return None

# Global MinIO client instance
minio_client = MinIOClient()