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
    ml,
    auth,
    learning,
    resource_preferences,
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


@app.on_event("startup")
def on_startup():
    from sqlalchemy import inspect, text
    from app.core.database import engine, Base
    try:
        # Create any newly defined tables
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            inspector = inspect(conn)
            if "users" in inspector.get_table_names():
                cols = [c["name"] for c in inspector.get_columns("users")]
                if "google_id" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(255)"))
                if "avatar_url" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(1024)"))
                if "password_hash" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
            if "roadmap_steps" in inspector.get_table_names():
                step_cols = [c["name"] for c in inspector.get_columns("roadmap_steps")]
                if "module_slug" not in step_cols:
                    conn.execute(text("ALTER TABLE roadmap_steps ADD COLUMN module_slug VARCHAR(100)"))
            if "assessments" in inspector.get_table_names():
                ass_cols = [c["name"] for c in inspector.get_columns("assessments")]
                if "role_id" not in ass_cols:
                    conn.execute(text("ALTER TABLE assessments ADD COLUMN role_id INTEGER REFERENCES roles(id)"))
            if "assessment_questions" in inspector.get_table_names():
                q_cols = [c["name"] for c in inspector.get_columns("assessment_questions")]
                if "skill_id" not in q_cols:
                    conn.execute(text("ALTER TABLE assessment_questions ADD COLUMN skill_id INTEGER REFERENCES skills(id)"))
            if "learning_modules" in inspector.get_table_names():
                lm_cols = [c["name"] for c in inspector.get_columns("learning_modules")]
                for col_name in [
                    "subtopics",
                    "why_it_matters_by_role",
                    "code_examples",
                    "quick_reference",
                    "level_variations",
                ]:
                    if col_name not in lm_cols:
                        conn.execute(text(f"ALTER TABLE learning_modules ADD COLUMN {col_name} TEXT"))
            conn.commit()

        # Ensure presentation learner and Analytics Engineer role are available
        from app.core.database import SessionLocal
        from app.models.user import User
        from app.models.role import Role
        from app.seed.seed_data import seed_database
        init_db = SessionLocal()
        try:
            ae_role = init_db.query(Role).filter_by(name="Analytics Engineer").first()
            nikil_user = init_db.query(User).filter_by(email="nikila.2509@gmail.com").first()
            if not ae_role or not nikil_user or nikil_user.target_role_id != (ae_role.id if ae_role else None):
                seed_database(init_db)
        finally:
            init_db.close()
    except Exception:
        pass

# Include API Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(learning.router, prefix=settings.API_V1_STR)
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
app.include_router(ml.router, prefix=settings.API_V1_STR)
app.include_router(resource_preferences.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "Welcome to SkillPath AI Backend API",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
