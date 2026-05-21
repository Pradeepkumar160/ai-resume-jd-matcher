"""
Skill extraction from resume/JD text.
Uses keyword matching against a comprehensive skills dictionary.
SpaCy is available for optional NER enrichment.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Comprehensive skills dictionary — add more as needed
SKILLS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    # Web frameworks
    "fastapi", "flask", "django", "express", "spring", "rails", "laravel",
    "nextjs", "nuxtjs", "angular", "vue", "react", "svelte",
    # Data & ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "xgboost", "lightgbm", "hugging face", "transformers", "bert", "gpt",
    "reinforcement learning", "neural network",
    # Databases
    "sql", "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "firebase", "supabase", "bigquery", "snowflake",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "jenkins", "ci/cd", "github actions", "gitlab ci",
    "linux", "bash", "shell scripting", "nginx", "apache",
    # Data Engineering
    "spark", "hadoop", "kafka", "airflow", "dbt", "flink", "databricks",
    "etl", "data pipeline", "data warehouse", "data lake",
    # Tools & Platforms
    "git", "github", "gitlab", "jira", "confluence", "notion",
    "streamlit", "gradio", "jupyter", "vscode",
    # Other
    "rest api", "graphql", "microservices", "agile", "scrum", "devops",
    "nodejs", "node.js", "vuejs", "reactjs",
]

# Sort by length descending so multi-word skills are matched first
SKILLS_SORTED = sorted(SKILLS, key=len, reverse=True)


def extract_skills(text: str) -> list[str]:
    """Extract known skills from text using keyword matching."""
    text_lower = text.lower()
    found = set()

    for skill in SKILLS_SORTED:
        # Use word-boundary matching to avoid false positives (e.g. "r" inside "for")
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill)

    return sorted(found)
