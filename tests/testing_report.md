# Testing Report — Member 13

## Scope

Two test files, run with `pytest`:

- `test_calculations.py` — unit tests for the analysis/risk_ai layer (Members 4-9)
- `test_apis.py` — integration tests for the FastAPI backend (Member 10), hitting the live endpoints via `TestClient`

## How to run

```bash
pip install -r backend/requirements.txt
cd Attandance-Tracker-main
pytest tests/ -v
```

## Results

**32 / 32 tests passed.**

| File | Tests | Passed |
|---|---|---|
| `test_calculations.py` | 22 | 22 |
| `test_apis.py` | 10 | 10 |

### `test_calculations.py` coverage
- `calculate_overall` / `calculate_subject_wise` — correct percentages on a known dataset, and a safe `0.0` for an unknown student ID
- `classify_trend` — all 4 trend labels (increasing / decreasing / stable / sudden_change), plus `insufficient_data` on too little data
- `analyze_trend` — returns the `trend_label` key the backend/dashboard depend on
- `_max_consecutive_absences` / `detect_absence_patterns` — correct streak counting, correct shape, safe defaults for an unknown student
- `classify_risk` — all 7 cases from the original Day-1 spec, plus the new `weak_subjects_count` escalation rule
- `generate_insight` — risk level appears in the output text, and absence/weak-subject clauses only appear when there's actually something to report

### `test_apis.py` coverage
- `/health` — returns healthy status
- `/students` — full list, plus filtering by `risk_level` and `department`
- `/student/{id}` — valid ID returns full profile; invalid ID returns 404
- `/attendance/{id}` — valid ID returns subject/weekly/monthly breakdowns as JSON lists (confirms the DataFrame→JSON fix works); invalid ID returns 404
- `/risk/{id}` — valid ID returns a risk level + non-empty AI insight string; invalid ID returns 404

## Known limitations
- Tests run against the live dataset (`data/attendance.csv`) rather than mocked data, so student-count/content assertions are intentionally loose (structure and status codes, not exact row counts) — this keeps tests stable if the dataset changes.
- No tests yet for the dashboard (Streamlit) or `risk_ai/ml_model.py` (the ML training script) — out of scope for this pass since neither exposes a stable API to test against.
