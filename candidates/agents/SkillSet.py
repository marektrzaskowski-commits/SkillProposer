from typing import List
from pydantic import BaseModel, Field


class SkillSet(BaseModel):
    skills: List[str] = Field(..., description="List of skills extracted from the job description")