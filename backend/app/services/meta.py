from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.database import SpecializationsReference, SkillsReference, InterestsReference
from app.schemas.meta import SpecializationSchema, InterestSchema, SkillSchema
from app.core.logging import logger

class MetaService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_specializations(self) -> list[SpecializationSchema]:
        try:
            stmt = select(SpecializationsReference).where(SpecializationsReference.is_active == True)
            result = await self._db.execute(stmt)
            specs = result.scalars().all()
            
            output = []
            for spec in specs:
                skill_stmt = select(SkillsReference).where(
                    SkillsReference.specialization_id == spec.id,
                    SkillsReference.is_active == True
                )
                skill_result = await self._db.execute(skill_stmt)
                skills = skill_result.scalars().all()
                
                output.append(SpecializationSchema(
                    id=spec.id,
                    code=spec.code,
                    name_en=spec.name_en,
                    name_vi=spec.name_vi,
                    skills=[SkillSchema.model_validate(s) for s in skills]
                ))
            return output
        except Exception as e:
            logger.error(f"Error in get_specializations: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error fetching specializations")

    async def get_interests(self) -> list[InterestSchema]:
        try:
            stmt = select(InterestsReference).where(InterestsReference.is_active == True)
            result = await self._db.execute(stmt)
            return [InterestSchema.model_validate(i) for i in result.scalars().all()]
        except Exception as e:
            logger.error(f"Error in get_interests: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error fetching interests")
