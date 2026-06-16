import asyncio
import sys
import uuid
from pathlib import Path

# Add the project root to sys.path so we can import app modules
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.database import Roles


ROLES_TO_SEED = [
    {
        "name": "student",
        "description": "Người dùng cuối đăng ký vào hệ thống để học."
    },
    {
        "name": "lecturer",
        "description": "Giảng viên, đối tác tạo nội dung trên nền tảng."
    },
    {
        "name": "admin",
        "description": "Quản trị viên cấp cao nhất (Super Admin)."
    },
    {
        "name": "moderator",
        "description": "Người kiểm duyệt nội dung (Khóa học, Review, Bình luận)."
    },
    {
        "name": "support",
        "description": "Chăm sóc khách hàng (CS)."
    },
    {
        "name": "finance",
        "description": "Kế toán, vận hành tài chính."
    }
]

async def seed_roles():
    print("Bắt đầu seed dữ liệu Roles...")
    async with AsyncSessionLocal() as session:
        for role_data in ROLES_TO_SEED:
            stmt = select(Roles).where(Roles.name == role_data["name"])
            result = await session.execute(stmt)
            existing_role = result.scalar_one_or_none()
            
            if existing_role:
                print(f"Role '{role_data['name']}' đã tồn tại, bỏ qua.")
            else:
                new_role = Roles(
                    id=uuid.uuid4(),
                    name=role_data["name"],
                    description=role_data["description"]
                )
                session.add(new_role)
                print(f"Đã thêm Role: '{role_data['name']}'")
        
        await session.commit()
    print("Seed dữ liệu Roles hoàn tất!")

if __name__ == "__main__":
    asyncio.run(seed_roles())
