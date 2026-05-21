import os
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MatchResult
from app.schemas import MatchHistoryItem, MatchResponse
from app.utils.embeddings import get_embedding
from app.utils.extractor import extract_skills
from app.utils.matcher import calculate_similarity
from app.utils.parser import extract_text_from_docx, extract_text_from_pdf
from app.utils.recommendations import generate_recommendations
from app.utils.scorer import skill_gap_analysis

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/match", response_model=MatchResponse)
async def match_resume(
    resume: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    job_description: str = Form(..., description="Paste the full job description"),
    candidate_name: str = Form(default="", description="Optional candidate name"),
    db: Session = Depends(get_db),
):
    # Validate file type
    filename = resume.filename or ""
    ext = os.path.splitext(filename)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Please upload a PDF or DOCX.",
        )

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    # Save uploaded file
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    try:
        contents = await resume.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

    # Extract text
    try:
        if ext == ".pdf":
            resume_text = extract_text_from_pdf(file_path)
        else:
            resume_text = extract_text_from_docx(file_path)
    except Exception as e:
        logger.error(f"Failed to extract text from resume: {e}")
        raise HTTPException(status_code=422, detail=f"Could not read resume file: {e}")

    if not resume_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Resume appears to be empty or could not be parsed.",
        )

    # NLP Processing
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    resume_embedding = get_embedding(resume_text)
    jd_embedding = get_embedding(job_description)

    score = calculate_similarity(resume_embedding, jd_embedding)
    matched_skills, missing_skills = skill_gap_analysis(resume_skills, jd_skills)
    recommendations = generate_recommendations(missing_skills)

    # Persist result
    try:
        record = MatchResult(
            candidate_name=candidate_name or None,
            resume_filename=safe_filename,
            score=score,
            matched_skills=", ".join(matched_skills),
            missing_skills=", ".join(missing_skills),
            recommendations=" | ".join(recommendations),
        )
        db.add(record)
        db.commit()
    except Exception as e:
        logger.warning(f"Could not save result to DB: {e}")
        db.rollback()

    return MatchResponse(
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        recommendations=recommendations,
    )


@router.get("/history", response_model=list[MatchHistoryItem])
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    """Return recent match results from the database."""
    records = (
        db.query(MatchResult)
        .order_by(MatchResult.created_at.desc())
        .limit(limit)
        .all()
    )
    results = []
    for r in records:
        results.append(
            MatchHistoryItem(
                id=r.id,
                candidate_name=r.candidate_name,
                resume_filename=r.resume_filename,
                score=r.score,
                matched_skills=[s.strip() for s in (r.matched_skills or "").split(",") if s.strip()],
                missing_skills=[s.strip() for s in (r.missing_skills or "").split(",") if s.strip()],
                recommendations=[s.strip() for s in (r.recommendations or "").split("|") if s.strip()],
                created_at=r.created_at,
            )
        )
    return results
