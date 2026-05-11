from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.meta import MetaService
from app.schemas.meta import SpecializationSchema, InterestSchema
from app.core.logging import logger

router = APIRouter(prefix="/meta", tags=["Metadata"])

@router.get("/specializations", response_model=list[SpecializationSchema])
async def get_specializations(db: AsyncSession = Depends(get_db)):
    try:
        service = MetaService(db)
        return await service.get_specializations()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_specializations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/interests", response_model=list[InterestSchema])
async def get_interests(db: AsyncSession = Depends(get_db)):
    try:
        service = MetaService(db)
        return await service.get_interests()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_interests: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
