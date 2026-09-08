# AI-Based Student Attendance Monitoring and Early-Warning System

5-Day Development Plan | 15-Member Team

## Folder → Team/Member Map

| Folder | Team | Members | Deliverables |
|---|---|---|---|
| `data/` | Team 1 | Member 1 – Dataset Developer | `attendance.csv` |
| `database/` | Team 1 | Member 2 – Database Developer, Member 3 – Data Preprocessing | `schema.sql`, `sample_queries.sql`, `data_preprocessing.py` |
| `analysis/` | Team 2 | Member 4 – Attendance Calculation, Member 5 – Trend Analysis, Member 6 – Absence Pattern Detection | `attendance_calculator.py`, `trend_analysis.py`, `absence_detection.py` |
| `risk_ai/` | Team 3 | Member 7 – Risk Assessment, Member 8 – Machine Learning, Member 9 – AI Insight Generation | `risk_engine.py`, `ml_model.py`, `insight_generator.py` |
| `backend/` | Team 4 | Member 10 – Backend Developer | Flask/FastAPI app + routes |
| `dashboard/` | Team 4 | Members 11–12 – Dashboard & Visualization | Streamlit app + components |
| `tests/` | Team 5 | Member 13 – Testing | Test cases + testing report |
| `.github/`, root files | Team 5 | Member 14 – Integration | GitHub repo setup, `.gitignore` |
| `docs/` | Team 5 | Member 15 – Documentation & Presentation | Report, PPT outline, screenshots |

## System Workflow

```
Attendance Data → Data Collection → Data Cleaning & Preprocessing →
Attendance Calculation → Pattern & Trend Detection → Risk Analysis →
AI Insight Generation → Mentor Dashboard
```

## Setup

```bash
git clone <repo-url>
cd attendance-system
pip install -r backend/requirements.txt
pip install -r dashboard/requirements.txt
```

## 5-Day Plan (summary)

- **Day 1:** Project structure, dataset, database design, dev environment ready.
- **Day 2:** Clean data → attendance calculations → trends → absence patterns → risk, working.
- **Day 3:** AI, backend, dashboard — working application prototype.
- **Day 4:** Full end-to-end integration + testing.
- **Day 5:** Finalisation, presentation, demo. No new features.
