def h_ledger(rows):
    parts = []
    for lbl, val in rows:
        parts.append(
            '<div class="lrow">'
            '<span class="ll">%s</span>'
            '<span class="lv">%s</span>'
            '</div>' % (lbl, val)
        )
    return '<div style="margin-bottom:1.8rem;">%s</div>' % "".join(parts)

def h_risk_bars(counts, total, risk_colors):
    parts = []
    for lvl in ["High", "Moderate", "Low"]:
        c   = counts.get(lvl, 0)
        pct = (c / total * 100) if total else 0
        col = risk_colors.get(lvl, "#000")
        parts.append(
            '<div class="rrow">'
            '<div class="rlbl">%s</div>'
            '<div class="rtrack">'
            '<div class="rfill" style="width:%.1f%%;background:%s;"></div>'
            '</div>'
            '<div class="rcnt">%d</div>'
            '</div>' % (lvl, pct, col, c)
        )
    return '<div style="margin-top:0.5rem;">%s</div>' % "".join(parts)

def h_stat(label, value):
    return (
        '<div class="stat-card">'
        '<div class="stat-label">%s</div>'
        '<div class="stat-value">%s</div>'
        '</div>' % (label, value)
    )
