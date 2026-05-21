from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MatchResponse(BaseModel):
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]


class MatchHistoryItem(BaseModel):
    id: int
    candidate_name: Optional[str]
    resume_filename: Optional[str]
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True
