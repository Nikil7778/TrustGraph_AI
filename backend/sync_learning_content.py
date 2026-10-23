"""
SkillPath AI - In-Place Learning Content Synchronization Script
Applies comprehensive, authoritative first-party curriculum content to learning_modules table.
GUARANTEE: Does NOT reset user progress, user skills, or evidence records.
"""

import sys
import json
import sqlite3
from typing import Dict, Any

from app.core.database import SessionLocal
from app.models.learning import LearningModule
from app.seed.comprehensive_learning_content import COMPREHENSIVE_MODULE_ENHANCEMENTS

def sync_learning_curriculum():
    db = SessionLocal()
    try:
        updated_count = 0
        total_words = 0
        print(f"Starting in-place curriculum synchronization for {len(COMPREHENSIVE_MODULE_ENHANCEMENTS)} modules...")
        
        for slug, data in COMPREHENSIVE_MODULE_ENHANCEMENTS.items():
            mod = db.query(LearningModule).filter(LearningModule.slug == slug).first()
            if not mod:
                print(f"  [SKIP] Module slug '{slug}' not found in database.")
                continue
                
            # Update title, concept name, difficulty, duration
            if "title" in data:
                mod.title = data["title"]
            if "concept_name" in data:
                mod.concept_name = data["concept_name"]
            if "difficulty" in data:
                mod.difficulty = data["difficulty"]
            if "estimated_minutes" in data:
                mod.estimated_minutes = data["estimated_minutes"]
                
            # Update learning objectives
            if "learning_objectives" in data:
                mod.learning_objectives = json.dumps(data["learning_objectives"])
                
            # Update comprehensive explanation
            if "explanation" in data:
                mod.explanation = data["explanation"]
                words = len(data["explanation"].split())
                total_words += words
                
            # Update structured worked example
            if "worked_example" in data:
                mod.worked_example = json.dumps(data["worked_example"])
                
            # Update common mistakes
            if "common_mistakes" in data:
                cm = data["common_mistakes"]
                mod.common_mistakes = json.dumps(cm) if isinstance(cm, (list, dict)) else str(cm)
                
            # Update guided & independent practice
            if "guided_practice" in data:
                mod.guided_practice = json.dumps(data["guided_practice"])
            if "independent_practice" in data:
                mod.independent_practice = json.dumps(data["independent_practice"])
                
            # Update concept check
            if "concept_check" in data:
                mod.concept_check = json.dumps(data["concept_check"])
                
            # Update applied role task
            if "applied_task" in data:
                mod.applied_task = json.dumps(data["applied_task"])
                
            # Update subtopics, role relevance, code examples, quick ref, level variations
            if "subtopics" in data:
                mod.subtopics = json.dumps(data["subtopics"])
            if "why_it_matters_by_role" in data:
                mod.why_it_matters_by_role = json.dumps(data["why_it_matters_by_role"])
            if "code_examples" in data:
                mod.code_examples = json.dumps(data["code_examples"])
            if "quick_reference" in data:
                mod.quick_reference = json.dumps(data["quick_reference"])
            if "level_variations" in data:
                mod.level_variations = json.dumps(data["level_variations"])
                
            updated_count += 1
            print(f"  [UPDATED] {slug}: '{mod.title}' (~{len(data.get('explanation', '').split())} words, {len(data.get('code_examples', []))} code examples)")
            
        db.commit()
        print(f"\nSuccessfully synchronized {updated_count} modules! Total explanation words: {total_words}")
    finally:
        db.close()

if __name__ == "__main__":
    sync_learning_curriculum()
