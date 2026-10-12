import sqlite3
from app.core.database import engine, Base
import app.models  # load all models

def migrate():
    Base.metadata.create_all(bind=engine)
    con = sqlite3.connect("skillpath.db")
    cur = con.cursor()
    
    # Check roadmaps columns
    cols_r = [c[1] for c in cur.execute("PRAGMA table_info(roadmaps)").fetchall()]
    if "regeneration_reason" not in cols_r:
        cur.execute("ALTER TABLE roadmaps ADD COLUMN regeneration_reason TEXT")
        print("Added regeneration_reason to roadmaps")
        
    # Check roadmap_steps columns
    cols_rs = [c[1] for c in cur.execute("PRAGMA table_info(roadmap_steps)").fetchall()]
    if "prerequisite_step_ids" not in cols_rs:
        cur.execute("ALTER TABLE roadmap_steps ADD COLUMN prerequisite_step_ids VARCHAR(255)")
        print("Added prerequisite_step_ids to roadmap_steps")
    if "evidence_required" not in cols_rs:
        cur.execute("ALTER TABLE roadmap_steps ADD COLUMN evidence_required TEXT")
        print("Added evidence_required to roadmap_steps")
    if "completed_at" not in cols_rs:
        cur.execute("ALTER TABLE roadmap_steps ADD COLUMN completed_at DATETIME")
        print("Added completed_at to roadmap_steps")
        
    con.commit()
    tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("Migration successful! Tables:", tables)
    con.close()

if __name__ == "__main__":
    migrate()
