import os
import pandas as pd
import numpy as np

def find_dataset_file():
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "cleaned_attendance_dataset.csv"),
        os.path.join(os.path.dirname(__file__), "..", "dataset", "cleaned_attendance_dataset.csv"),
        r"c:\Users\HP\Downloads\cleaned_attendance_dataset (2) (1).csv",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return os.path.abspath(p)
    raise FileNotFoundError("Could not locate cleaned_attendance_dataset.csv")

def load_dataset(filepath=None):
    if filepath is None:
        filepath = find_dataset_file()

    raw_df = pd.read_csv(filepath)
    raw_df['date'] = pd.to_datetime(raw_df['date'])

    # Weight status: Present/On Duty = 1.0, Late = 0.5, Absent = 0.0
    status_weights = {'Present': 1.0, 'On Duty': 1.0, 'Late': 0.5, 'Absent': 0.0}
    valid_df = raw_df[raw_df['status'].isin(status_weights.keys())].copy()
    valid_df['weight'] = valid_df['status'].map(status_weights)

    # Student summary aggregation
    students = valid_df.groupby(['student_id', 'student_name', 'department', 'year', 'section']).agg(
        total_sessions=('status', 'count'),
        presents=('status', lambda s: (s == 'Present').sum()),
        absents=('status', lambda s: (s == 'Absent').sum()),
        lates=('status', lambda s: (s == 'Late').sum()),
        on_duties=('status', lambda s: (s == 'On Duty').sum()),
        score=('weight', 'sum')
    ).reset_index()

    students['attendance_rate'] = (students['score'] / students['total_sessions'] * 100).round(1)

    def calc_risk(att):
        if att < 70.0:
            return 'High'
        elif att < 85.0:
            return 'Medium'
        else:
            return 'Low'

    students['risk_level'] = students['attendance_rate'].apply(calc_risk)

    def calc_gpa(sid):
        seed = sum(ord(c) for c in sid)
        rng = np.random.default_rng(seed)
        return round(float(rng.uniform(2.4, 3.95)), 2)

    students['gpa'] = students['student_id'].apply(calc_gpa)
    students['name'] = students['student_name']
    students['major'] = students['department']
    students['recent_absences'] = students['absents']

    # Trailing daily trend
    daily_trend = valid_df.groupby('date')['weight'].agg(['sum', 'count']).reset_index()
    daily_trend['pct'] = (daily_trend['sum'] / daily_trend['count'] * 100).round(1)
    daily_trend = daily_trend.sort_values('date')

    return students, raw_df, daily_trend

def get_student_subjects(raw_df, student_id):
    status_weights = {'Present': 1.0, 'On Duty': 1.0, 'Late': 0.5, 'Absent': 0.0}
    valid_df = raw_df[(raw_df['student_id'] == student_id) & (raw_df['status'].isin(status_weights.keys()))].copy()
    if valid_df.empty:
        return pd.DataFrame()
    valid_df['weight'] = valid_df['status'].map(status_weights)

    subj = valid_df.groupby('subject').agg(
        total_classes=('status', 'count'),
        presents=('status', lambda s: (s == 'Present').sum()),
        absents=('status', lambda s: (s == 'Absent').sum()),
        lates=('status', lambda s: (s == 'Late').sum()),
        score=('weight', 'sum')
    ).reset_index()

    subj['attendance_rate'] = (subj['score'] / subj['total_classes'] * 100).round(1)
    return subj.sort_values('attendance_rate', ascending=True)

def get_student_timeline(raw_df, student_id):
    status_weights = {'Present': 1.0, 'On Duty': 1.0, 'Late': 0.5, 'Absent': 0.0}
    valid_df = raw_df[(raw_df['student_id'] == student_id) & (raw_df['status'].isin(status_weights.keys()))].copy()
    if valid_df.empty:
        return pd.DataFrame()
    valid_df['weight'] = valid_df['status'].map(status_weights)
    daily = valid_df.groupby('date')['weight'].agg(['sum', 'count']).reset_index()
    daily['pct'] = (daily['sum'] / daily['count'] * 100).round(1)
    return daily.sort_values('date')
