from __future__ import annotations

import os
import shutil
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import UploadFile
from app.core.config import settings
from app.core.logging import logger


class BaseStorage(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile, folder: str) -> str:
        """Upload file và trả về đường dẫn/URL."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Xóa file."""
        pass


class LocalStorage(BaseStorage):
    def __init__(self, base_dir: str = "uploads", base_url: str = "/uploads") -> None:
        self.base_dir = Path(base_dir)
        self.base_url = base_url
        # Đảm bảo thư mục gốc tồn tại
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, file: UploadFile, folder: str) -> str:
        # 1. Tạo thư mục con nếu chưa có (avatars, thumbnails, v.v.)
        target_dir = self.base_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)

        # 2. Tạo tên file duy nhất để tránh trùng lặp
        ext = os.path.splitext(file.filename or "")[1]
        unique_name = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}{ext}"
        
        file_path = target_dir / unique_name
        
        # 3. Lưu file xuống đĩa
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info("storage.local_upload_success", path=str(file_path))
            
            # Trả về đường dẫn tương đối để lưu vào DB
            # Ví dụ: /uploads/avatars/abc.png
            return f"{self.base_url}/{folder}/{unique_name}"
        except Exception as e:
            logger.error("storage.local_upload_error", error=str(e))
            raise e

    async def delete(self, path: str) -> bool:
        # Convert URL path sang local path
        # /uploads/avatars/abc.png -> uploads/avatars/abc.png
        relative_path = path.lstrip("/")
        if relative_path.startswith("uploads/"):
            relative_path = relative_path.replace("uploads/", "", 1)
        
        full_path = self.base_dir / relative_path
        
        try:
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error("storage.local_delete_error", path=path, error=str(e))
            return False


class StorageService:
    """
    Orchestrator cho Storage.
    Dễ dàng switch giữa Local, S3, R2 bằng cách thay đổi provider.
    """
    def __init__(self, provider: BaseStorage | None = None) -> None:
        # Mặc định dùng LocalStorage nếu không truyền provider
        self.provider = provider or LocalStorage(
            base_dir=settings.UPLOAD_DIR,
            base_url=settings.UPLOAD_URL
        )

    async def upload_avatar(self, file: UploadFile) -> str:
        try:
            return await self.provider.upload(file, "avatars")
        except Exception as e:
            logger.error(f"Error in upload_avatar: {str(e)}", exc_info=True)
            raise

    async def upload_thumbnail(self, file: UploadFile) -> str:
        try:
            return await self.provider.upload(file, "course_thumbnails")
        except Exception as e:
            logger.error(f"Error in upload_thumbnail: {str(e)}", exc_info=True)
            raise

    async def upload_chat_image(self, file: UploadFile) -> str:
        try:
            return await self.provider.upload(file, "chat_images")
        except Exception as e:
            logger.error(f"Error in upload_chat_image: {str(e)}", exc_info=True)
            raise

    async def delete_file(self, path: str) -> bool:
        try:
            return await self.provider.delete(path)
        except Exception as e:
            logger.error(f"Error in delete_file: {str(e)}", exc_info=True)
            return False
