import asyncio
import sys
import uuid
from pathlib import Path

# Add the project root to sys.path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.database import Users, Roles, UserRoles
from app.core.security import hash_password

async def create_super_admin():
    email = "admin@gmail.com"
    password = "Huynh@2004"
    
    print(f"Đang tạo tài khoản Admin: {email}...")
    
    async with AsyncSessionLocal() as session:
        # 1. Check if user already exists
        stmt = select(Users).where(Users.email == email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("User đã tồn tại. Đang cập nhật mật khẩu...")
            user_id = existing_user.id
            existing_user.password_hash = hash_password(password)
        else:
            print("Đang tạo user mới...")
            user_id = uuid.uuid4()
            new_user = Users(
                id=user_id,
                email=email,
                password_hash=hash_password(password),
                full_name="Super Admin",
                status="ACTIVE",
                is_verified=True,
                is_profile_completed=True
            )
            session.add(new_user)
            
        # 2. Assign admin role
        stmt_role = select(Roles).where(Roles.name == "admin")
        result_role = await session.execute(stmt_role)
        admin_role = result_role.scalar_one_or_none()
        
        if not admin_role:
            print("Lỗi: Role 'admin' chưa tồn tại. Vui lòng chạy seed_roles.py trước.")
            return
            
        # Check if user already has admin role
        stmt_user_role = select(UserRoles).where(
            UserRoles.user_id == user_id, 
            UserRoles.role_id == admin_role.id
        )
        result_ur = await session.execute(stmt_user_role)
        if not result_ur.scalar_one_or_none():
            print("Đang gán role 'admin' cho user...")
            new_ur = UserRoles(user_id=user_id, role_id=admin_role.id)
            session.add(new_ur)
        else:
            print("User đã có role 'admin'.")
            
        await session.commit()
        print("✅ Hoàn tất! Quản trị viên đã sẵn sàng.")
        print(f"Email: {email}")
        print(f"Password: {password}")

if __name__ == "__main__":
    asyncio.run(create_super_admin())
