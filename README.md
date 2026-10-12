# SkillPath AI — Evidence-Driven Career Intelligence Platform

> *"The learner does not follow the roadmap. The roadmap follows the learner."*

SkillPath AI is an enterprise-grade career intelligence and learning analytics platform. It replaces static curriculum paths with deterministic competence tracking, diagnosing skill debt, prioritizing high-value career gaps, and dynamically reshaping learning roadmaps based on evaluated real-world execution.

---

## 🚀 Key Features

### 1. Daily Analytics Dashboard
- **Career Readiness & Target Role**: Quantitative benchmark progress for target roles (e.g., Data Analyst).
- **Next-Best-Proof**: Deterministic recommendation of the single highest-leverage learning activity to prove competence.
- **Biggest Career Gaps vs. Immediate Roadmap**: Ranked skill deficits contrasted with dynamic sequential milestones.
- **Recruiter Evidence Ledger**: Live ledger tracking verified evaluations and scores.

### 2. Skill DNA (Competency Matrix)
- Multi-dimensional competency evaluation tracking demonstrated skill levels, deterministic confidence, and supporting evidence counts.
- Semantic indicators distinguishing **Verified**, **Developing**, and **Skill Debt** statuses.
- Detailed diagnostic inspector modal with breakdown metrics and conceptual AI explanations.

### 3. Skill Debt Diagnostic Engine
- Detects the divergence between theoretical multiple-choice knowledge and practical code execution.
- Highlights execution divergence gaps (e.g., academic test vs. practical SQL code execution).
- Actionable rescue practice recommendations to eliminate technical debt before tackling advanced concepts.

### 4. Adaptive Dynamic Roadmap
- Sequential, automated roadmap graph that rebuilds dynamically whenever new proof or skill debt is recorded.
- Visual timeline rail illustrating completed milestones, actively inserted rescue practice steps, and upcoming concepts.
- Re-route rationale tracking downstream rework hours saved.

### 5. Practice Lab & Industry Failure Lab
- Interactive sandbox environment with realistic schemas (e.g., e-commerce customer returns).
- Live execution editor with 4-pillar automated evaluation (Data correctness, syntax, performance, business logic).
- Hint system and failure analysis to reinforce edge-case handling.

### 6. Proof-of-Skill Passport
- Recruiter-ready, verifiable skill transcript connecting every claimed skill to evaluated evidence items.
- Dual-mode perspective (Learner View vs. Recruiter View) with tamper-evident proof records and export capability.

### 7. Floating AI Career Coach
- Persistent, globally available assistant accessible from anywhere in the application via a fixed floating trigger.
- System-aware guidance powered by Gemini with direct read-only access to live backend state (Skill DNA, Skill Debt, Next-Best-Proof, Roadmap).
- Contextual awareness adapting suggestions based on the currently viewed page.

---

## 🛠️ Architecture & Tech Stack

### Frontend
- **Framework**: Next.js 16 (Turbopack, App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS (Stitch-inspired clean white SaaS design system)
- **State Management**: React Context (`LearnerContext`, `CoachContext`)
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.12)
- **ORM / Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (prod)
- **Deterministic Engines**:
  - `SkillDNAEngine` — Multi-factor confidence & evidence scoring
  - `SkillDebtEngine` — Execution vs. quiz divergence diagnostics
  - `CareerValueEngine` — Role relevance and impact weight calculation
  - `NextBestProofEngine` — Top action selection algorithm
  - `RoadmapEngine` — Graph re-ordering and dynamic insertion
- **AI Integration**: Google Gemini (strictly bounded for explanations, hints, and coaching dialogue)

---

## 🏁 Getting Started

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+
- Git

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI documentation will be available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The application will be live at `http://localhost:3000`.

---

## 🧪 Testing

### Backend Unit & Integration Tests
```bash
cd backend
venv\Scripts\python.exe test_phase15.py
venv\Scripts\python.exe test_coach.py
venv\Scripts\python.exe test_phase14.py
```

### Frontend Validation & Production Build
```bash
cd frontend
npx tsc --noEmit
npm run build
```

---

## 📄 License
MIT License.
