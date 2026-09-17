import streamlit as st
from components.overview_cards import h_ledger
from components.charts import make_chart
from data import get_student_timeline, get_student_subjects

def render_student_detail(sid, students, raw_df, risk_colors):
    matches = students[students.student_id == sid]
    if matches.empty:
        st.error(f"Student ID {sid} not found.")
        if st.button("Back to student list"):
            st.session_state.student = None
            st.rerun()
        return

    row = matches.iloc[0]
    col = risk_colors.get(row["risk_level"], "#000")

    if st.button("Back to student list"):
        st.session_state.student = None
        st.rerun()

    st.write("")
    st.html(
        '<div class="rec-hdr">'
        '<div class="rec-name">%s</div>'
        '<div class="rec-meta">%s &middot; %s &middot; Year %s (Sec %s)</div>'
        '<span class="risk-tag" style="background:%s;">%s Risk</span>'
        '</div>'
        % (row["name"], row["student_id"], row["department"], row["year"], row["section"], col, row["risk_level"])
    )

    rec_col, chart_col = st.columns([1, 1.4], gap="large")
    with rec_col:
        st.html('<p class="slbl" style="margin-top:0.2rem;">Record Summary</p><hr class="hairline">')
        st.html(h_ledger([
            ("Attendance rate",  "%.1f%%" % row["attendance_rate"]),
            ("Total Sessions",   str(row["total_sessions"])),
            ("Absences",         str(row["recent_absences"])),
            ("Late Count",       str(row["lates"])),
            ("GPA",              "%.2f"   % row["gpa"]),
            ("Department",       row["department"]),
            ("Risk level",       row["risk_level"]),
        ]))

    with chart_col:
        st.html('<p class="slbl" style="margin-top:0.2rem;">Student Attendance Timeline</p><hr class="hairline">')
        timeline = get_student_timeline(raw_df, sid)
        if not timeline.empty:
            make_chart(timeline["date"], timeline["pct"], f"detail_timeline_{sid}", height=260)
        else:
            st.info("No timeline data recorded for this student.")

    # Subject Breakdown
    st.html('<p class="slbl" style="margin-top:2rem;">Subject Breakdown</p><hr class="hairline">')
    subj_df = get_student_subjects(raw_df, sid)
    if not subj_df.empty:
        st.dataframe(
            subj_df[["subject", "total_classes", "presents", "lates", "absents", "attendance_rate"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "subject":          "Subject Name",
                "total_classes":    "Total Classes",
                "presents":         "Present",
                "lates":            "Late",
                "absents":          "Absent",
                "attendance_rate":  st.column_config.NumberColumn("Attendance Rate", format="%.1f%%"),
            }
        )
    else:
        st.caption("No subject breakdown available.")
