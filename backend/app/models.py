from sqlalchemy import Column, DateTime, Integer, String, Float, Text, func
from app.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=True)
    resume_filename = Column(String, nullable=True)
    score = Column(Float, nullable=False)
    matched_skills = Column(Text, nullable=True)   # comma-separated
    missing_skills = Column(Text, nullable=True)   # comma-separated
    recommendations = Column(Text, nullable=True)  # pipe-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
