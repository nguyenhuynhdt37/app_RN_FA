import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

# Data to seed
SPECIALIZATIONS = [
    {'code': 'IT', 'en': 'Information Technology', 'vi': 'Công nghệ Thông tin'},
    {'code': 'ECONOMICS', 'en': 'Economics & Management', 'vi': 'Kinh tế & Quản trị'},
    {'code': 'EDUCATION', 'en': 'Education', 'vi': 'Sư phạm'},
    {'code': 'ENGLISH', 'en': 'English Language', 'vi': 'Ngôn ngữ Anh'},
    {'code': 'MEDICINE', 'en': 'General Medicine', 'vi': 'Y đa khoa'},
    {'code': 'AUTOMOTIVE', 'en': 'Automotive Engineering', 'vi': 'Kỹ thuật Ô tô'},
    {'code': 'OTHER', 'en': 'Other', 'vi': 'Khác'},
]

SKILLS = {
    'IT': [
        {'en': 'Python Programming', 'vi': 'Lập trình Python'},
        {'en': 'Javascript Programming', 'vi': 'Lập trình Javascript'},
        {'en': 'React Native', 'vi': 'React Native'},
        {'en': 'DevOps', 'vi': 'DevOps'},
        {'en': 'Cybersecurity', 'vi': 'Bảo mật mạng'},
        {'en': 'Database', 'vi': 'Cơ sở dữ liệu'},
    ],
    'ECONOMICS': [
        {'en': 'Marketing', 'vi': 'Marketing'},
        {'en': 'Finance', 'vi': 'Tài chính'},
        {'en': 'Leadership', 'vi': 'Lãnh đạo'},
        {'en': 'HR Management', 'vi': 'Quản trị nhân sự'},
        {'en': 'Business Strategy', 'vi': 'Chiến lược kinh doanh'},
    ],
    'EDUCATION': [
        {'en': 'Teaching Skills', 'vi': 'Kỹ năng giảng dạy'},
        {'en': 'Educational Tech', 'vi': 'Công nghệ giáo dục'},
        {'en': 'Child Psychology', 'vi': 'Tâm lý trẻ em'},
        {'en': 'Curriculum Design', 'vi': 'Thiết kế bài giảng'},
    ],
    'ENGLISH': [
        {'en': 'IELTS', 'vi': 'Chứng chỉ IELTS'},
        {'en': 'TOEIC', 'vi': 'Chứng chỉ TOEIC'},
        {'en': 'Translation', 'vi': 'Biên phiên dịch'},
        {'en': 'Business English', 'vi': 'Tiếng Anh thương mại'},
        {'en': 'Public Speaking', 'vi': 'Thuyết trình'},
    ],
    'MEDICINE': [
        {'en': 'First Aid', 'vi': 'Sơ cấp cứu'},
        {'en': 'Anatomy', 'vi': 'Giải phẫu học'},
        {'en': 'Pharmacology', 'vi': 'Dược lý học'},
        {'en': 'Clinical Skills', 'vi': 'Kỹ năng lâm sàng'},
    ],
    'AUTOMOTIVE': [
        {'en': 'Engine Diagnostics', 'vi': 'Chẩn đoán động cơ'},
        {'en': 'Auto CAD', 'vi': 'Auto CAD'},
        {'en': 'Electric Vehicles', 'vi': 'Xe điện'},
        {'en': 'Maintenance', 'vi': 'Bảo dưỡng ô tô'},
    ],
    'OTHER': [
        {'en': 'Problem Solving', 'vi': 'Giải quyết vấn đề'},
        {'en': 'Critical Thinking', 'vi': 'Tư duy phản biện'},
        {'en': 'Project Management', 'vi': 'Quản lý dự án'},
        {'en': 'Soft Skills', 'vi': 'Kỹ năng mềm'},
    ]
}

INTERESTS = [
    {'en': 'Artificial Intelligence (AI)', 'vi': 'Trí tuệ nhân tạo (AI)'},
    {'en': 'Mobile Development', 'vi': 'Phát triển Mobile'},
    {'en': 'Blockchain', 'vi': 'Blockchain'},
    {'en': 'E-commerce', 'vi': 'Thương mại điện tử'},
    {'en': 'Content Creation', 'vi': 'Sáng tạo nội dung'},
    {'en': 'Entrepreneurship', 'vi': 'Khởi nghiệp'},
]

async def seed():
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Clear old data
        await session.execute(text("TRUNCATE TABLE public.specializations_reference CASCADE"))
        await session.execute(text("TRUNCATE TABLE public.interests_reference CASCADE"))

        # Seed Specializations
        for spec in SPECIALIZATIONS:
            spec_id = uuid.uuid4()
            await session.execute(
                text("INSERT INTO public.specializations_reference (id, code, name_en, name_vi) VALUES (:id, :code, :en, :vi)"),
                {'id': spec_id, 'code': spec['code'], 'en': spec['en'], 'vi': spec['vi']}
            )
            
            # Seed Skills for this specialization
            if spec['code'] in SKILLS:
                for skill in SKILLS[spec['code']]:
                    await session.execute(
                        text("INSERT INTO public.skills_reference (specialization_id, name_en, name_vi) VALUES (:spec_id, :en, :vi)"),
                        {'spec_id': spec_id, 'en': skill['en'], 'vi': skill['vi']}
                    )

        # Seed Interests
        for interest in INTERESTS:
            await session.execute(
                text("INSERT INTO public.interests_reference (name_en, name_vi) VALUES (:en, :vi)"),
                {'en': interest['en'], 'vi': interest['vi']}
            )

        await session.commit()
    print("✅ Seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed())
