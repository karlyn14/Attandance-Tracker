"""
Member 3 - Data Preprocessing
Day 1: Build the cleaning pipeline using dummy rows with intentional errors.
Day 2: Point this at the real data/attendance.csv from Member 1 - no code
       changes needed since the column format is identical.
"""

import re
import pandas as pd
import numpy as np

VALID_STATUSES = {"Present", "Absent"}
STUDENT_ID_PATTERN = re.compile(r"^S\w*\d+$")  # must start with 'S' and end in digits (covers S101, STU0001, ...)


def load_and_clean(csv_path: str) -> pd.DataFrame:
    """
    Reads a raw attendance CSV and returns a cleaned DataFrame.

    Cleaning steps (in order):
      1. Load CSV
      2. Drop exact duplicate rows
      3. Parse dates -> invalid dates become NaT -> those rows dropped
      4. Drop rows with missing values in required columns
      5. Drop rows whose student_id doesn't match the expected pattern (S + digits)
      6. Drop rows whose status isn't exactly 'Present' or 'Absent'
      7. Drop/flag rows with missing subject info
    """
    df = pd.read_csv(csv_path)

    report = {"rows_loaded": len(df)}

    # 2. Duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_dropped"] = before - len(df)

    # 3. Invalid dates -> coerce to NaT, then drop
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["date"])
    report["invalid_dates_dropped"] = before - len(df)

    # 4. Missing values in any required column (besides date, already handled)
    required_cols = ["student_id", "student_name", "department", "year",
                      "section", "subject", "period", "status"]
    before = len(df)
    df = df.dropna(subset=required_cols)
    # also treat empty strings as missing
    for col in required_cols:
        if df[col].dtype == object:
            df = df[df[col].astype(str).str.strip() != ""]
    report["missing_values_dropped"] = before - len(df)

    # 5. Invalid student IDs
    before = len(df)
    df = df[df["student_id"].astype(str).str.match(STUDENT_ID_PATTERN)]
    report["invalid_student_ids_dropped"] = before - len(df)

    # 6. Invalid status values
    before = len(df)
    df = df[df["status"].isin(VALID_STATUSES)]
    report["invalid_status_dropped"] = before - len(df)

    # 7. Missing subject info (already caught by required_cols, kept as explicit
    #    check in case subject contains only whitespace or a placeholder)
    before = len(df)
    df = df[df["subject"].astype(str).str.strip() != ""]
    report["missing_subject_dropped"] = before - len(df)

    report["rows_remaining"] = len(df)

    print("Cleaning report:")
    for k, v in report.items():
        print(f"  {k}: {v}")

    return df.reset_index(drop=True)


if __name__ == "__main__":
    cleaned = load_and_clean("attendance.csv")  # Member 1's raw file
    print("\nCleaned data (first 10 rows):")
    print(cleaned.head(10))

    cleaned.to_csv("cleaned_attendance.csv", index=False)
    print("\nSaved -> cleaned_attendance.csv")
