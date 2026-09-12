"""
Member 6 - Absence Pattern Detection
=====================================
Flags risky absence patterns beyond just the overall absence %.

Detections implemented (per spec):
    1. Frequent absences        -> overall absence rate > threshold (default 20%)
    2. Consecutive absences     -> longest streak of consecutive 'Absent' rows (by date, per student)
    3. Subject-wise absenteeism -> a subject's absence rate for a student is much higher than
                                    that student's overall absence rate
    4. Day-wise absenteeism     -> absences clustering on a specific weekday
    5. Sudden absence spikes    -> last 1-2 weeks absence rate vs. the student's prior average
"""

import argparse
from dataclasses import dataclass, field
import pandas as pd

# --------------------------------------------------------------------------
# Config / thresholds - tweak these as needed
# --------------------------------------------------------------------------
FREQUENT_ABSENCE_THRESHOLD = 0.20     
CONSECUTIVE_ABSENCE_THRESHOLD = 3     
SUBJECT_ABSENCE_MULTIPLIER = 1.5      
SUBJECT_MIN_RECORDS = 3               
DAYWISE_MULTIPLIER = 1.5              
DAYWISE_MIN_ABSENCES = 3              
SPIKE_WINDOW_DAYS = 14                
SPIKE_MULTIPLIER = 1.5                
SPIKE_MIN_PRIOR_RECORDS = 5           

# --------------------------------------------------------------------------
# Data loading / cleaning
# --------------------------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["status"] = df["status"].astype(str).str.strip()
    df = df.dropna(subset=["date", "student_id", "status"])
    return df

# --------------------------------------------------------------------------
# 1. Frequent absences
# --------------------------------------------------------------------------
def flag_frequent_absences(df: pd.DataFrame, threshold: float = FREQUENT_ABSENCE_THRESHOLD) -> pd.DataFrame:
    grp = df.groupby("student_id")
    total = grp.size()
    absent = grp.apply(lambda g: (g["status"] == "Absent").sum())
    rate = (absent / total).rename("absence_rate")

    out = pd.DataFrame({
        "total_records": total,
        "total_absences": absent,
        "absence_rate": rate,
    })
    out["flag_frequent_absence"] = out["absence_rate"] > threshold
    return out.reset_index()

# --------------------------------------------------------------------------
# 2. Consecutive absences
# --------------------------------------------------------------------------
def _max_consecutive_absences(statuses: pd.Series) -> int:
    max_streak = 0
    current = 0
    for s in statuses:
        if s == "Absent":
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 0
    return max_streak

def flag_consecutive_absences(df: pd.DataFrame, threshold: int = CONSECUTIVE_ABSENCE_THRESHOLD) -> pd.DataFrame:
    records = []
    for student_id, g in df.sort_values("date").groupby("student_id"):
        streak = _max_consecutive_absences(g["status"].tolist())
        records.append({"student_id": student_id, "max_consecutive_absences": streak})

    out = pd.DataFrame(records)
    out["flag_consecutive_absence"] = out["max_consecutive_absences"] >= threshold
    return out

# --------------------------------------------------------------------------
# 3. Subject-wise absenteeism
# --------------------------------------------------------------------------
def flag_subject_absenteeism(
    df: pd.DataFrame,
    multiplier: float = SUBJECT_ABSENCE_MULTIPLIER,
    min_records: int = SUBJECT_MIN_RECORDS,
) -> pd.DataFrame:
    overall = df.groupby("student_id").apply(
        lambda g: (g["status"] == "Absent").sum() / len(g)
    ).rename("overall_absence_rate")

    subj = df.groupby(["student_id", "subject"]).apply(
        lambda g: pd.Series({
            "subject_records": len(g),
            "subject_absences": (g["status"] == "Absent").sum(),
            "subject_absence_rate": (g["status"] == "Absent").sum() / len(g),
        })
    ).reset_index()

    subj = subj.merge(overall, on="student_id", how="left")
    subj["flag_subject_absenteeism"] = (
        (subj["subject_records"] >= min_records)
        & (subj["overall_absence_rate"] > 0)
        & (subj["subject_absence_rate"] > subj["overall_absence_rate"] * multiplier)
    )
    return subj

# --------------------------------------------------------------------------
# 4. Day-wise absenteeism
# --------------------------------------------------------------------------
def flag_daywise_absenteeism(
    df: pd.DataFrame,
    multiplier: float = DAYWISE_MULTIPLIER,
    min_absences: int = DAYWISE_MIN_ABSENCES,
) -> pd.DataFrame:
    df = df.copy()
    df["day_name"] = df["date"].dt.day_name()

    records = []
    for student_id, g in df.groupby("student_id"):
        total_by_day = g["day_name"].value_counts()
        absent_g = g[g["status"] == "Absent"]
        total_absences = len(absent_g)
        if total_absences < min_absences:
            continue
        absent_by_day = absent_g["day_name"].value_counts()

        for day, day_absences in absent_by_day.items():
            day_total = total_by_day.get(day, 0)
            if day_total == 0:
                continue
            day_absence_rate = day_absences / day_total
            expected_share = day_total / len(g) 
            actual_share = day_absences / total_absences 

            flagged = actual_share > expected_share * multiplier and day_absences >= 2
            records.append({
                "student_id": student_id,
                "day_name": day,
                "day_absences": day_absences,
                "day_total_classes": day_total,
                "day_absence_rate": day_absence_rate,
                "flag_daywise_absenteeism": flagged,
            })

    return pd.DataFrame(records)

# --------------------------------------------------------------------------
# 5. Sudden absence spikes
# --------------------------------------------------------------------------
def flag_absence_spikes(
    df: pd.DataFrame,
    window_days: int = SPIKE_WINDOW_DAYS,
    multiplier: float = SPIKE_MULTIPLIER,
    min_prior_records: int = SPIKE_MIN_PRIOR_RECORDS,
) -> pd.DataFrame:
    max_date = df["date"].max()
    cutoff = max_date - pd.Timedelta(days=window_days)

    records = []
    for student_id, g in df.groupby("student_id"):
        recent = g[g["date"] > cutoff]
        prior = g[g["date"] <= cutoff]

        if len(prior) < min_prior_records or len(recent) == 0:
            continue

        recent_rate = (recent["status"] == "Absent").sum() / len(recent)
        prior_rate = (prior["status"] == "Absent").sum() / len(prior)

        flagged = prior_rate == 0 and recent_rate > 0 and len(recent) >= 2
        if prior_rate > 0:
            flagged = recent_rate > prior_rate * multiplier

        records.append({
            "student_id": student_id,
            "recent_records": len(recent),
            "recent_absence_rate": recent_rate,
            "prior_records": len(prior),
            "prior_absence_rate": prior_rate,
            "flag_absence_spike": flagged,
        })

    return pd.DataFrame(records)

# --------------------------------------------------------------------------
# Combine everything into one summary per student
# --------------------------------------------------------------------------
def run_all_checks(df: pd.DataFrame) -> dict:
    return {
        "frequent_absences": flag_frequent_absences(df),
        "consecutive_absences": flag_consecutive_absences(df),
        "subject_absenteeism": flag_subject_absenteeism(df),
        "daywise_absenteeism": flag_daywise_absenteeism(df),
        "absence_spikes": flag_absence_spikes(df),
    }

def build_student_summary(results: dict) -> pd.DataFrame:
    freq = results["frequent_absences"][["student_id", "absence_rate", "flag_frequent_absence"]]
    cons = results["consecutive_absences"][["student_id", "max_consecutive_absences", "flag_consecutive_absence"]]

    subj_flag = (
        results["subject_absenteeism"]
        .groupby("student_id")["flag_subject_absenteeism"]
        .any()
        .rename("flag_subject_absenteeism")
        .reset_index()
    )

    day_flag = (
        results["daywise_absenteeism"]
        .groupby("student_id")["flag_daywise_absenteeism"]
        .any()
        .rename("flag_daywise_absenteeism")
        .reset_index()
        if not results["daywise_absenteeism"].empty
        else pd.DataFrame(columns=["student_id", "flag_daywise_absenteeism"])
    )

    spike = results["absence_spikes"][["student_id", "flag_absence_spike"]]

    summary = freq.merge(cons, on="student_id", how="outer")
    summary = summary.merge(subj_flag, on="student_id", how="left")
    summary = summary.merge(day_flag, on="student_id", how="left")
    summary = summary.merge(spike, on="student_id", how="left")

    flag_cols = [
        "flag_frequent_absence",
        "flag_consecutive_absence",
        "flag_subject_absenteeism",
        "flag_daywise_absenteeism",
        "flag_absence_spike",
    ]
    for c in flag_cols:
        summary[c] = summary[c].fillna(False)

    summary["risk_flags_count"] = summary[flag_cols].sum(axis=1)
    summary["at_risk"] = summary["risk_flags_count"] > 0

    return summary.sort_values("risk_flags_count", ascending=False).reset_index(drop=True)

# --------------------------------------------------------------------------
# Dummy student test 
# --------------------------------------------------------------------------
def make_dummy_data() -> pd.DataFrame:
    rows = [
        {"student_id": "DUMMY001", "student_name": "Test Student", "department": "TEST",
         "year": 1, "section": "A", "subject": "Math", "date": "2026-01-05", "period": 1, "status": "Absent"},
        {"student_id": "DUMMY001", "student_name": "Test Student", "department": "TEST",
         "year": 1, "section": "A", "subject": "Math", "date": "2026-01-06", "period": 1, "status": "Absent"},
        {"student_id": "DUMMY001", "student_name": "Test Student", "department": "TEST",
         "year": 1, "section": "A", "subject": "Math", "date": "2026-01-07", "period": 1, "status": "Absent"},
        {"student_id": "DUMMY001", "student_name": "Test Student", "department": "TEST",
         "year": 1, "section": "A", "subject": "Math", "date": "2026-01-08", "period": 1, "status": "Present"},
        {"student_id": "DUMMY001", "student_name": "Test Student", "department": "TEST",
         "year": 1, "section": "A", "subject": "Science", "date": "2026-01-09", "period": 2, "status": "Present"},
        {"student_id": "DUMMY002", "student_name": "Control Student", "department": "TEST",
         "year": 1, "section": "A", "subject": "Math", "date": "2026-01-05", "period": 1, "status": "Present"},
        {"student_id": "DUMMY002", "student_name": "Control Student", "department": "TEST",
         "year": 1, "section": "A", "subject": "Math", "date": "2026-01-06", "period": 1, "status": "Present"},
        {"student_id": "DUMMY002", "student_name": "Control Student", "department": "TEST",
         "year": 1, "section": "A", "subject": "Science", "date": "2026-01-07", "period": 2, "status": "Present"},
    ]
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df

def run_dummy_test():
    print("=" * 60)
    print("DUMMY DATA TEST")
    print("=" * 60)
    df = make_dummy_data()
    results = run_all_checks(df)

    print("\n[Consecutive absences]")
    print(results["consecutive_absences"])

    dummy_row = results["consecutive_absences"].loc[
        results["consecutive_absences"]["student_id"] == "DUMMY001"
    ]
    assert dummy_row["max_consecutive_absences"].iloc[0] == 3, "Expected 3 consecutive absences for DUMMY001"
    assert dummy_row["flag_consecutive_absence"].iloc[0] == True, "DUMMY001 should be flagged"
    print("\n[OK] Dummy student DUMMY001 correctly detected with 3 consecutive absences.")

    control_row = results["consecutive_absences"].loc[
        results["consecutive_absences"]["student_id"] == "DUMMY002"
    ]
    assert control_row["flag_consecutive_absence"].iloc[0] == False, "DUMMY002 should NOT be flagged"
    print("[OK] Control student DUMMY002 correctly NOT flagged.")
    print("=" * 60 + "\n")

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Absence pattern detection")
    parser.add_argument("--input", type=str, help="Path to cleaned attendance CSV")
    parser.add_argument("--dummy-test", action="store_true", help="Run the dummy-student test first")
    parser.add_argument("--output", type=str, default="absence_flags_summary.csv",
                         help="Where to write the per-student summary CSV")
    args = parser.parse_args()

    if args.dummy_test:
        run_dummy_test()

    if args.input:
        df = load_data(args.input)
        print(f"Loaded {len(df)} rows for {df['student_id'].nunique()} students from {args.input}\n")

        results = run_all_checks(df)
        summary = build_student_summary(results)

        print("=" * 60)
        print("REAL DATA - TOP AT-RISK STUDENTS (by number of flags triggered)")
        print("=" * 60)
        print(summary.head(15).to_string(index=False))

        summary.to_csv(args.output, index=False)
        print(f"\nFull per-student summary written to: {args.output}")

        results["subject_absenteeism"][results["subject_absenteeism"]["flag_subject_absenteeism"]] \
            .to_csv("absence_flags_subjectwise.csv", index=False)
        results["daywise_absenteeism"][results["daywise_absenteeism"]["flag_daywise_absenteeism"]] \
            .to_csv("absence_flags_daywise.csv", index=False)
        print("Detail flags written to: absence_flags_subjectwise.csv, absence_flags_daywise.csv")
    elif not args.dummy_test:
        parser.print_help()

if __name__ == "__main__":
    main()
