from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import (
    health,
    users,
    roles,
    skills,
    assessments,
    projects,
    roadmap,
    skill_dna,
    skill_debt,
    career_value,
    next_best_proof,
    industry_labs,
    ai,
    dashboard,
    skill_passport,
    demo,
    coach,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="SkillPath AI Backend API — Evidence-driven Data Science career learning platform source of truth.",
)

# Configure CORS Middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(roles.router, prefix=settings.API_V1_STR)
app.include_router(skills.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(assessments.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(roadmap.router, prefix=settings.API_V1_STR)
app.include_router(skill_dna.router, prefix=settings.API_V1_STR)
app.include_router(skill_debt.router, prefix=settings.API_V1_STR)
app.include_router(career_value.router, prefix=settings.API_V1_STR)
app.include_router(next_best_proof.router, prefix=settings.API_V1_STR)
app.include_router(industry_labs.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(skill_passport.router, prefix=settings.API_V1_STR)
app.include_router(demo.router, prefix=settings.API_V1_STR)
app.include_router(coach.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "Welcome to SkillPath AI Backend API",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
