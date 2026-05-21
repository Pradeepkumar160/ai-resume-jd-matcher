# Skill-specific recommendations — extend this dict as needed
SKILL_TIPS: dict[str, str] = {
    "docker": "Learn Docker by containerising a personal project. Try the official 'Get Started' tutorial.",
    "kubernetes": "Study Kubernetes with Minikube locally. The CKA certification is highly valued.",
    "aws": "Start with AWS Free Tier. Focus on EC2, S3, Lambda, and RDS for most job requirements.",
    "python": "Build 2–3 Python projects and publish them on GitHub with clear READMEs.",
    "machine learning": "Take Andrew Ng's ML Specialization on Coursera and build a Kaggle project.",
    "deep learning": "Complete fast.ai or DeepLearning.AI courses, then fine-tune a pre-trained model.",
    "sql": "Practice on LeetCode Database problems and build a mini analytics dashboard.",
    "react": "Build a full-stack CRUD app with React + a REST API to demonstrate end-to-end skills.",
    "fastapi": "Create a production-grade REST API with auth, DB, and Dockerise it.",
    "git": "Contribute to an open-source project to show collaborative Git workflow skills.",
    "tensorflow": "Complete TensorFlow Developer Certificate program and build a model deployed to an API.",
    "pytorch": "Implement a paper from scratch in PyTorch and post it on GitHub.",
}

DEFAULT_TIP = "Add a project, course certification, or work experience that demonstrates {skill}."


def generate_recommendations(missing_skills: list[str]) -> list[str]:
    """Generate actionable improvement suggestions for each missing skill."""
    recommendations = []
    for skill in missing_skills:
        tip = SKILL_TIPS.get(
            skill.lower(),
            DEFAULT_TIP.format(skill=skill),
        )
        recommendations.append(f"📌 {skill.title()}: {tip}")
    return recommendations
