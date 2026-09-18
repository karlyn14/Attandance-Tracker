TREND_PHRASES = {
    "increasing": "an improving",
    "decreasing": "a declining",
    "stable": "a stable",
    "sudden_change": "a suddenly fluctuating",
    "fluctuating": "an inconsistent",
    "insufficient_data": "an unclear (not enough data yet)",
}


def generate_insight(student_name: str, overall_pct: float, trend_label: str,
                      consecutive_absences: int, weak_subjects: list, risk_level: str) -> str:
    """Fills a template string with the student's stats."""
    trend_phrase = TREND_PHRASES.get(trend_label, trend_label)
    intro = f"{student_name}'s attendance is currently {overall_pct:.1f}% and has shown {trend_phrase} trend."

    extra_clauses = []
    if consecutive_absences > 0:
        plural = "s" if consecutive_absences != 1 else ""
        verb = "were" if consecutive_absences != 1 else "was"
        extra_clauses.append(f"{consecutive_absences} consecutive absence{plural} {verb} detected")
    if weak_subjects:
        subj_str = ", ".join(weak_subjects)
        verb = "show" if len(weak_subjects) != 1 else "shows"
        extra_clauses.append(f"{subj_str} {verb} particularly low attendance")

    if extra_clauses:
        extra_sentence = ". ".join(c[0].upper() + c[1:] for c in extra_clauses)
        extra_sentence = extra_sentence.rstrip(".") + "."
        sentence = f"{intro} {extra_sentence} Risk level: {risk_level}."
    else:
        sentence = f"{intro} Risk level: {risk_level}."

    return " ".join(sentence.split())


if __name__ == "__main__":
    print(generate_insight("Rahul Kumar", 73, "decreasing", 3, ["Mathematics"], "High"))
    print(generate_insight("Divya Rao", 92, "stable", 0, [], "Low"))
    print(generate_insight("Arjun Kumar", 80, "sudden_change", 1, ["Physics", "Chemistry"], "Moderate"))
