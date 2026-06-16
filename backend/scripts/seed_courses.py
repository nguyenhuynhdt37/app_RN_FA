import asyncio
import uuid
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.database import Users, CourseCategories, Courses, Sections, LearningUnits, LearningBlocks, CourseLevel

async def seed_data():
    async with AsyncSessionLocal() as db:
        # 1. Get an admin or user to be instructor
        res = await db.execute(select(Users).limit(1))
        user = res.scalar_one_or_none()
        if not user:
            print("No users found. Please register a user first.")
            return

        # 2. Create Category
        category = CourseCategories(
            name_vi="Tiếng Anh",
            name_en="English",
            icon_url="https://img.icons8.com/color/96/great-britain-circular.png",
            position=1
        )
        db.add(category)
        await db.flush()

        # 3. Create Course
        course = Courses(
            category_id=category.id,
            instructor_id=user.id,
            created_by=user.id,
            title="IELTS Speaking Masterclass",
            slug="ielts-speaking-masterclass",
            description="Chinh phục IELTS Speaking 8.5 cùng chuyên gia.",
            thumbnail_url="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2071&auto=format&fit=crop",
            level=CourseLevel.INTERMEDIATE,
            language="vi",
            tags=["ielts", "speaking", "english"],
            learning_outcomes=["Biết cách trả lời Part 1, 2, 3", "Luyện phản xạ tự nhiên"],
            prerequisites=["Level B1 trở lên"],
            difficulty_score=7,
            is_published=True
        )
        db.add(course)
        await db.flush()

        # 4. Create Section
        section = Sections(
            course_id=course.id,
            title="Chương 1: Giới thiệu & Part 1",
            position=1
        )
        db.add(section)
        await db.flush()

        # 5. Create Unit
        unit = LearningUnits(
            section_id=section.id,
            title="Bài 1: Tổng quan về IELTS Speaking",
            position=1,
            is_free=True
        )
        db.add(unit)
        await db.flush()

        # 6. Create Blocks
        block_video = LearningBlocks(
            unit_id=unit.id,
            block_type="VIDEO",
            position=1,
            content={
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Video giới thiệu",
                "duration": 120
            }
        )
        block_text = LearningBlocks(
            unit_id=unit.id,
            block_type="TEXT",
            position=2,
            content={
                "text": "Chào mừng bạn đến với khóa học. Đây là bài học đầu tiên giúp bạn hiểu rõ cấu trúc bài thi."
            }
        )
        db.add_all([block_video, block_text])
        
        await db.commit()
        print(f"Seed success! Course: {course.title}")

if __name__ == "__main__":
    asyncio.run(seed_data())
