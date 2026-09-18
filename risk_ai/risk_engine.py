NEGATIVE_TRENDS = {"decreasing", "sudden_change"}
CONSECUTIVE_ABSENCE_HIGH_RISK = 3


def classify_risk(overall_pct: float, trend_label: str, consecutive_absences: int,
                   weak_subjects_count: int = 0) -> str:
    """Returns 'Low', 'Moderate', or 'High'."""

    # High risk conditions
    if overall_pct < 75:
        return "High"
    if trend_label == "decreasing" and overall_pct < 85:
        return "High"
    if consecutive_absences >= CONSECUTIVE_ABSENCE_HIGH_RISK:
        return "High"
    if weak_subjects_count >= 2:
        return "High"

    # Moderate risk conditions
    if 75 <= overall_pct <= 84:
        return "Moderate"
    if trend_label in NEGATIVE_TRENDS:
        return "Moderate"
    if weak_subjects_count == 1:
        return "Moderate"

    # Otherwise Low
    if overall_pct >= 85 and trend_label not in NEGATIVE_TRENDS:
        return "Low"

    return "Moderate"  # safe default


def assess_student(overall_pct: float, trend_label: str, consecutive_absences: int,
                    weak_subjects_count: int = 0) -> dict:
    return {
        "overall_pct": overall_pct,
        "trend": trend_label,
        "consecutive_absences": consecutive_absences,
        "weak_subjects_count": weak_subjects_count,
        "risk_level": classify_risk(overall_pct, trend_label, consecutive_absences, weak_subjects_count),
    }


if __name__ == "__main__":
    test_cases = [
        (90, "stable", 0, "Low"),
        (86, "increasing", 1, "Low"),
        (80, "stable", 1, "Moderate"),
        (87, "decreasing", 1, "Moderate"),
        (73, "decreasing", 3, "High"),
        (60, "stable", 0, "High"),
        (90, "stable", 4, "High"),
    ]
    for pct, trend, cons, expected in test_cases:
        result = classify_risk(pct, trend, cons)
        status = "OK" if result == expected else "MISMATCH"
        print(f"[{status}] classify_risk({pct}, '{trend}', {cons}) = {result} (expected {expected})")
