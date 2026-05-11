from pydantic import BaseModel, ConfigDict
import uuid

class SkillSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name_en: str
    name_vi: str

class SpecializationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    code: str
    name_en: str
    name_vi: str
    skills: list[SkillSchema] = []

class InterestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name_en: str
    name_vi: str
