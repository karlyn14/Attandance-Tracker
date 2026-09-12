
TREND_PHRASES = {
    "increasing": "an improving",
    "decreasing": "a declining",
    "stable": "a stable",
    "sudden_change": "a suddenly fluctuating",
    "insufficient_data": "an unclear (not enough data yet)",
}


def generate_insight(student_id: str, overall_pct: float, trend: str,
                      consecutive_absences: int, weak_subject: str, risk_level: str) -> str:
    """Fills a template string with the student's stats."""
    trend_phrase = TREND_PHRASES.get(trend, trend)

    intro = f"Student {student_id}'s attendance is currently {overall_pct}% and has shown {trend_phrase} trend."

    extra_clauses = []
    if consecutive_absences > 0:
        plural = "s" if consecutive_absences != 1 else ""
        verb = "were" if consecutive_absences != 1 else "was"
        extra_clauses.append(
            f"{consecutive_absences} consecutive absence{plural} {verb} detected"
        )
    if weak_subject and str(weak_subject).lower() != "nan":
        extra_clauses.append(f"{weak_subject} has particularly low attendance")

    if extra_clauses:
        extra_sentence = " ".join(c[0].upper() + c[1:] for c in extra_clauses)
        extra_sentence = extra_sentence.rstrip(".") + "."
        # join two clauses naturally with 'and' when there are exactly two
        if len(extra_clauses) == 2:
            extra_sentence = f"{extra_clauses[0]}, and {extra_clauses[1]}."
            extra_sentence = extra_sentence[0].upper() + extra_sentence[1:]
        sentence = f"{intro} {extra_sentence} Risk level: {risk_level}."
    else:
        sentence = f"{intro} Risk level: {risk_level}."

    return " ".join(sentence.split())


def generate_insight_for_student(student_id: str, df, calculate_overall, calculate_subject_wise,
                                  analyze_student_trend, max_consecutive_absences, classify_risk) -> str:
    """Convenience wrapper that pulls live numbers from Members 4-7's
    modules and produces the final sentence. Pass in the functions to
    avoid tight coupling / circular imports."""
    overall = calculate_overall(student_id, df)
    trend_info = analyze_student_trend(student_id, df)
    consecutive = max_consecutive_absences(student_id, df)
    subj_df = calculate_subject_wise(student_id, df)
    weak_subject = subj_df.iloc[0]["subject"] if len(subj_df) else "N/A"
    risk = classify_risk(overall, trend_info["trend"], consecutive)

    return generate_insight(student_id, overall, trend_info["trend"], consecutive, weak_subject, risk)


if __name__ == "__main__":
    # Day 1 dummy test
    print(generate_insight("S103", 73, "decreasing", 3, "Mathematics", "High"))
    print(generate_insight("S201", 92, "stable", 0, None, "Low"))
    print(generate_insight("S305", 80, "sudden_change", 1, "Physics", "Moderate"))

    # Day 3+ real wiring test
    import sys, os
    import pandas as pd
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analysis"))
    from attendance_calculator import calculate_overall, calculate_subject_wise
    from trend_analysis import analyze_student_trend
    from absence_detection import max_consecutive_absences
    from risk_engine import classify_risk

    df = pd.read_csv("../data/attendance_clean.csv")
    for sid in df["student_id"].unique()[:3]:
        print(generate_insight_for_student(
            sid, df, calculate_overall, calculate_subject_wise,
            analyze_student_trend, max_consecutive_absences, classify_risk,
        ))

   
