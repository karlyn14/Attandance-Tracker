import os
import plotly.graph_objects as go
import streamlit as st

def setup_theme():
    os.makedirs(".streamlit", exist_ok=True)
    config_path = ".streamlit/config.toml"
    theme_content = """[theme]
base = "light"
primaryColor = "#A9812E"
backgroundColor = "#F3F3EF"
secondaryBackgroundColor = "#EAEBE6"
textColor = "#16213E"
font = "sans serif"
"""
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(theme_content)


INK        = "#16213E"
INK_SOFT   = "#5a6370"
PAPER_CARD = "#EAEBE6"
RULE       = "#CACCC6"
BRASS      = "#A9812E"

def make_chart(x, y, key, height=280):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers",
        line=dict(color=INK, width=2.2),
        marker=dict(size=4, color=BRASS),
        fill="tozeroy",
        fillcolor="rgba(22,33,62,0.08)",
        hovertemplate="%{x|%b %d, %Y}<br>Attendance: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor  = PAPER_CARD,
        paper_bgcolor = "rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color=INK_SOFT, size=12),
        margin=dict(l=4, r=4, t=8, b=4),
        height=height,
        xaxis=dict(showgrid=False, showline=True, linecolor=RULE, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor=RULE, ticksuffix="%", tickfont=dict(size=11), range=[0, 105]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False}, key=key)
