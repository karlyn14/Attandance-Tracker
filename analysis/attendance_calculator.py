import pandas as pd

DATA_FILE = "cleaned_attendance_dataset.csv"

def _prepare(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["is_present"] = df["status"].str.strip().str.lower().eq("present")
    return df

def calculate_overall(student_id, df):
    df = _prepare(df)
    student = df[df["student_id"] == student_id]
    total = len(student)
    present = student["is_present"].sum()
    return (present / total * 100) if total else 0.0

def calculate_subject_wise(student_id, df):
    df = _prepare(df)
    student = df[df["student_id"] == student_id]
    result = student.groupby("subject")["is_present"].agg(["sum", "count"])
    result["attendance_pct"] = result["sum"] / result["count"] * 100
    result = result.rename(columns={"sum": "present_classes", "count": "total_classes"})
    return result.reset_index()

def calculate_weekly(student_id, df):
    df = _prepare(df)
    student = df[df["student_id"] == student_id].copy()
    student["week"] = student["date"].dt.isocalendar().week.astype(int)
    result = student.groupby("week")["is_present"].agg(["sum", "count"])
    result["attendance_pct"] = result["sum"] / result["count"] * 100
    return result.rename(columns={"sum": "present_classes", "count": "total_classes"}).reset_index()

def calculate_monthly(student_id, df):
    df = _prepare(df)
    student = df[df["student_id"] == student_id].copy()
    student["month"] = student["date"].dt.month
    result = student.groupby("month")["is_present"].agg(["sum", "count"])
    result["attendance_pct"] = result["sum"] / result["count"] * 100
    return result.rename(columns={"sum": "present_classes", "count": "total_classes"}).reset_index()

if __name__ == "__main__":
    df = pd.read_csv(DATA_FILE)

    # Sanity check using the first 3 students in the cleaned dataset.
    sample_students = df["student_id"].drop_duplicates().head(3)

    for student_id in sample_students:
        print(f"\n{student_id} - Overall: {calculate_overall(student_id, df):.2f}%")
        print("Subject-wise:")
        print(calculate_subject_wise(student_id, df).to_string(index=False))
        print("Weekly:")
        print(calculate_weekly(student_id, df).to_string(index=False))
        print("Monthly:")
        print(calculate_monthly(student_id, df).to_string(index=False))
