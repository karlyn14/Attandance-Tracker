"""
risk_ai/ml_model.py
Member 8 - Machine Learning
AI-Based Student Attendance Monitoring and Early-Warning System

Day 1: Pipeline built and validated on a hand-made dummy feature table.
Day 3: Swap `load_features()` to pull real features from Members 4-6's
       outputs (attendance_calculator.py, trend_analysis.py,
       absence_detection.py) instead of the dummy table below, then retrain.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# ---------------------------------------------------------------------------
# 1. Feature table
# ---------------------------------------------------------------------------
def load_dummy_features() -> pd.DataFrame:
    """
    Hand-made dummy feature table for Day 1 pipeline testing.
    Columns match what Members 4-6 will eventually produce:
      - overall_attendance     : float, %  (Member 4)
      - weekly_attendance      : float, %  (Member 4, most recent week)
      - attendance_change      : float, % change week-over-week (Member 5)
      - absence_frequency      : float, %  total absences (Member 6)
      - consecutive_absences   : int       max consecutive Absent streak (Member 6)
      - subject_attendance     : float, %  lowest subject-wise attendance (Member 6)
      - risk_level             : label     Low / Moderate / High (ground truth for training)
    """
    data = [
        # overall, weekly, change, abs_freq, consec_abs, subject_att, risk
        [92, 90, +1, 8, 0, 88, "Low"],
        [88, 85, -2, 12, 1, 82, "Low"],
        [95, 96, +1, 4, 0, 91, "Low"],
        [86, 84, -1, 14, 1, 80, "Low"],
        [90, 91, +0, 9, 0, 85, "Low"],
        [80, 78, -3, 20, 2, 72, "Moderate"],
        [77, 74, -4, 22, 2, 70, "Moderate"],
        [75, 73, -2, 24, 2, 68, "Moderate"],
        [82, 79, -3, 18, 1, 74, "Moderate"],
        [78, 76, -2, 21, 2, 71, "Moderate"],
        [65, 60, -8, 35, 4, 55, "High"],
        [70, 65, -10, 30, 3, 58, "High"],
        [60, 55, -12, 40, 5, 50, "High"],
        [73, 68, -9, 28, 3, 60, "High"],
        [68, 62, -11, 33, 4, 52, "High"],
        [58, 50, -15, 45, 6, 48, "High"],
    ]
    columns = [
        "overall_attendance",
        "weekly_attendance",
        "attendance_change",
        "absence_frequency",
        "consecutive_absences",
        "subject_attendance",
        "risk_level",
    ]
    return pd.DataFrame(data, columns=columns)


def load_real_features(csv_path: str) -> pd.DataFrame:
    """
    Once Members 4-6 publish a merged feature CSV (one row per student,
    same 6 feature columns + risk_level), just point this at it directly:
        return pd.read_csv(csv_path)

    Until that lands, this builds the same feature table straight from
    the raw per-record attendance CSV (student_id, student_name,
    department, year, section, subject, date, period, status), so the
    pipeline can already run on real data.
    """
    raw = pd.read_csv(csv_path)
    raw["date"] = pd.to_datetime(raw["date"])
    raw = raw.sort_values(["student_id", "date", "period"])

    # "Unknown" rows are missing/unreliable records - drop from rate calcs.
    # "On Duty" counts as attended (excused, not absent).
    valid = raw[raw["status"] != "Unknown"].copy()
    valid["attended"] = valid["status"].isin(["Present", "Late", "On Duty"]).astype(int)
    valid["is_absent"] = (valid["status"] == "Absent").astype(int)

    iso = valid["date"].dt.isocalendar()
    valid["week_key"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)

    rows = []
    for sid, g in valid.groupby("student_id"):
        overall = g["attended"].mean() * 100
        absence_freq = g["is_absent"].mean() * 100

        weekly = g.groupby("week_key")["attended"].mean().sort_index() * 100
        weekly_att = weekly.iloc[-1] if len(weekly) >= 1 else overall
        change = weekly.iloc[-1] - weekly.iloc[-2] if len(weekly) >= 2 else 0

        # longest run of consecutive Absent records, in chronological order
        seq = g.sort_values(["date", "period"])["is_absent"].tolist()
        max_streak = cur = 0
        for v in seq:
            cur = cur + 1 if v == 1 else 0
            max_streak = max(max_streak, cur)

        subj_att = g.groupby("subject")["attended"].mean().min() * 100

        rows.append([
            sid, round(overall, 1), round(weekly_att, 1), round(change, 1),
            round(absence_freq, 1), max_streak, round(subj_att, 1),
        ])

    feat = pd.DataFrame(rows, columns=[
        "student_id", "overall_attendance", "weekly_attendance", "attendance_change",
        "absence_frequency", "consecutive_absences", "subject_attendance",
    ])

    # Rule-based label until real ground-truth risk labels exist.
    def label(row):
        if row["overall_attendance"] < 75 or row["consecutive_absences"] >= 4:
            return "High"
        elif row["overall_attendance"] < 85:
            return "Moderate"
        return "Low"

    feat["risk_level"] = feat.apply(label, axis=1)
    return feat.drop(columns=["student_id"])


# ---------------------------------------------------------------------------
# 2. Train / evaluate
# ---------------------------------------------------------------------------
def train_and_evaluate(df: pd.DataFrame):
    feature_cols = [
        "overall_attendance",
        "weekly_attendance",
        "attendance_change",
        "absence_frequency",
        "consecutive_absences",
        "subject_attendance",
    ]
    X = df[feature_cols]
    y = df["risk_level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("=== ML Model Pipeline ===")
    print(f"Train rows: {len(X_train)}  Test rows: {len(X_test)}\n")

    print(f"Accuracy : {accuracy_score(y_test, y_pred):.2f}")
    print(f"Precision: {precision_score(y_test, y_pred, average='macro', zero_division=0):.2f}")
    print(f"Recall   : {recall_score(y_test, y_pred, average='macro', zero_division=0):.2f}")
    print(f"F1 Score : {f1_score(y_test, y_pred, average='macro', zero_division=0):.2f}")

    print("\nConfusion Matrix (rows=actual, cols=predicted):")
    labels = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print(pd.DataFrame(cm, index=labels, columns=labels))

    print("\nFull classification report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    return model


# ---------------------------------------------------------------------------
# 3. Predict for a single student (used later by Member 9 / backend API)
# ---------------------------------------------------------------------------
def predict_risk(model, overall_attendance, weekly_attendance, attendance_change,
                  absence_frequency, consecutive_absences, subject_attendance):
    row = pd.DataFrame([{
        "overall_attendance": overall_attendance,
        "weekly_attendance": weekly_attendance,
        "attendance_change": attendance_change,
        "absence_frequency": absence_frequency,
        "consecutive_absences": consecutive_absences,
        "subject_attendance": subject_attendance,
    }])
    return model.predict(row)[0]


if __name__ == "__main__":
    # --- Real dataset (cleaned_attendance_dataset.csv) ---
    df = load_real_features("cleaned_attendance_dataset (2).csv")

    # --- Fallback: dummy data, if no real dataset is available yet ---
    # df = load_dummy_features()

    model = train_and_evaluate(df)

    # quick sanity check prediction
    sample_pred = predict_risk(model, 73, 68, -9, 28, 3, 60)
    print(f"\nSample prediction for a 73% attendance, declining student: {sample_pred}")
