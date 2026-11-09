
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from html import escape

st.set_page_config(
    page_title="VERSE | NHL Intelligence",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------
# THEME
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"], [data-testid="stApp"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #090F1D;
    color: #F1F5F9;
}
.block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
#MainMenu, footer {visibility: hidden;}
h1, h2, h3 {letter-spacing: -0.035em;}
[data-testid="stMetric"] {
    background: #131F32;
    border: 1px solid #24344B;
    padding: 20px;
    border-radius: 14px;
}
[data-testid="stMetricLabel"] {color: #94A3B8;}
[data-testid="stMetricValue"] {color: #F8FAFC;}
[data-testid="stTabs"] button {font-weight: 600;}
[data-testid="stDataFrame"] {
    border: 1px solid #24344B;
    border-radius: 12px;
}
.stButton > button, .stDownloadButton > button {
    background: #193D32;
    color: #86EFAC;
    border: 1px solid #28634D;
    border-radius: 10px;
    font-weight: 700;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #4ADE80;
    color: white;
}
.verse-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 22px;
    border-bottom: 1px solid #253249;
    margin-bottom: 30px;
}
.verse-logo {
    font-size: 34px;
    font-weight: 900;
    letter-spacing: -2px;
    color: #F8FAFC;
}
.verse-logo span {color: #4ADE80;}
.verse-subtitle {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.2px;
}
.live-pill {
    background: #123B2E;
    color: #86EFAC;
    border: 1px solid #28634D;
    padding: 8px 13px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 700;
}
.section-label {
    color: #4ADE80;
    font-size: 12px;
    letter-spacing: 2px;
    font-weight: 800;
    margin-bottom: 8px;
}
.hero-title {
    color: #F8FAFC;
    font-size: clamp(30px, 5vw, 46px);
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1.15;
}
.muted {color: #94A3B8; font-size: 13px;}
.kpi {
    background: #131F32;
    border: 1px solid #24344B;
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0 20px;
}
.kpi-label {
    font-size: 11px;
    color: #94A3B8;
    font-weight: 700;
    letter-spacing: 1px;
}
.kpi-value {
    font-size: 31px;
    font-weight: 800;
    color: #F8FAFC;
    margin-top: 8px;
}
.kpi-value.green {color: #4ADE80;}
.pick-card {
    background: linear-gradient(135deg, #152238, #101B2C);
    border: 1px solid #293B54;
    border-radius: 18px;
    padding: 22px;
    margin: 12px 0;
}
.pick-card:hover {border-color: #3F785D;}
.pick-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.team-name {
    color: #F8FAFC;
    font-size: 22px;
    font-weight: 800;
}
.matchup {
    color: #94A3B8;
    font-size: 12px;
    margin-top: 5px;
}
.roi-badge {
    background: #123D30;
    border: 1px solid #28634D;
    color: #86EFAC;
    padding: 10px 14px;
    border-radius: 12px;
    text-align: center;
    font-weight: 800;
    font-size: 18px;
    white-space: nowrap;
}
.roi-badge.negative {
    background: #40222A;
    border-color: #713844;
    color: #FDA4AF;
}
.roi-small {
    font-size: 9px;
    letter-spacing: 1px;
    font-weight: 600;
}
.prob-track {
    background: #29374C;
    height: 8px;
    border-radius: 20px;
    overflow: hidden;
    margin: 12px 0 18px;
}
.prob-fill {
    background: linear-gradient(90deg, #16A34A, #86EFAC);
    height: 100%;
    border-radius: 20px;
}
.stats-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    border-top: 1px solid #29374C;
    padding-top: 15px;
}
.stat-label {
    color: #94A3B8;
    font-size: 10px;
    margin-bottom: 6px;
}
.stat-value {
    color: #F8FAFC;
    font-size: 17px;
    font-weight: 700;
}
.green-text {color: #86EFAC;}
.red-text {color: #FDA4AF;}
.goalie-line {
    color: #94A3B8;
    font-size: 12px;
    margin-top: 15px;
}
.section-heading {
    font-size: 22px;
    font-weight: 800;
    color: #F8FAFC;
    margin: 22px 0 8px;
}
.disclaimer {
    color: #64748B;
    font-size: 11px;
    border-top: 1px solid #253249;
    padding-top: 18px;
    margin-top: 30px;
}
@media (max-width: 600px) {
    .block-container {padding: 1.1rem;}
    .pick-card {padding: 15px;}
    .team-name {font-size: 18px;}
    .stat-value {font-size: 14px;}
    .kpi {padding: 14px;}
    .kpi-value {font-size: 24px;}
}
</style>
""", unsafe_allow_html=True)


# ---------------------------
# DATA HELPERS
# ---------------------------
def numeric(value, default=0.0):
    try:
        result = pd.to_numeric(value, errors="coerce")
        if pd.isna(result):
            return default
        return float(result)
    except (TypeError, ValueError):
        return default


def txt(value, fallback="—"):
    if value is None or pd.isna(value):
        return fallback
    value = str(value).strip()
    return escape(value) if value else fallback


def odds_label(value):
    number = numeric(value, None)
    if number is None:
        return "—"
    return f"+{number:.0f}" if number > 0 else f"{number:.0f}"


def percentage(value):
    return f"{numeric(value):.2f}%"


def metric_card(label, value, green=False):
    css = "green" if green else ""
    st.markdown(
        f'<div class="kpi">'
        f'<div class="kpi-label">{escape(str(label))}</div>'
        f'<div class="kpi-value {css}">{escape(str(value))}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300)
def load_predictions():
    files = sorted(Path("reports").glob("nhl_fanduel_*.csv"))
    if not files:
        return pd.DataFrame(), None
    latest = files[-1]
    return pd.read_csv(latest), latest


@st.cache_data(ttl=300)
def load_history():
    path = Path("history/predictions.csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def pick_card(row):
    team = txt(row.get("team"))
    matchup = txt(row.get("matchup"))
    side = txt(row.get("side"))
    goalie = txt(row.get("projected_goalie"))

    win = numeric(row.get("model_win_pct"))
    edge = numeric(row.get("edge_pp"))
    roi = numeric(row.get("expected_roi_pct"))
    odds = odds_label(row.get("fanduel_us_ml"))

    bar_width = max(0, min(100, win))
    positive = roi > 0
    badge_class = "" if positive else "negative"
    edge_class = "green-text" if edge > 0 else "red-text"

    st.markdown(f"""
    <div class="pick-card">
        <div class="pick-top">
            <div>
                <div class="team-name">{team}</div>
                <div class="matchup">{matchup} · {side}</div>
            </div>
            <div class="roi-badge {badge_class}">
                {roi:+.2f}%
                <div class="roi-small">EXPECTED ROI</div>
            </div>
        </div>
        <div style="margin-top:20px;display:flex;
                    justify-content:space-between;gap:10px;">
            <span class="muted">MODEL WIN PROBABILITY</span>
            <strong>{win:.2f}%</strong>
        </div>
        <div class="prob-track">
            <div class="prob-fill" style="width:{bar_width:.2f}%"></div>
        </div>
        <div class="stats-row">
            <div>
                <div class="stat-label">FANDUEL ODDS</div>
                <div class="stat-value">{odds}</div>
            </div>
            <div>
                <div class="stat-label">MODEL EDGE</div>
                <div class="stat-value {edge_class}">{edge:+.2f} pp</div>
            </div>
            <div>
                <div class="stat-label">MARKET WIN %</div>
                <div class="stat-value">{percentage(row.get("no_vig_market_pct"))}</div>
            </div>
        </div>
        <div class="goalie-line">🥅 Projected goalie: {goalie}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------
# HEADER
# ---------------------------
st.markdown("""
<div class="verse-header">
    <div>
        <div class="verse-logo">VER<span>SE</span></div>
        <div class="verse-subtitle">NHL INTELLIGENCE PLATFORM</div>
    </div>
    <div class="live-pill">● MODEL DASHBOARD</div>
</div>
""", unsafe_allow_html=True)

df, report_file = load_predictions()
history = load_history()

tabs = st.tabs([
    "🏒 Today's Picks",
    "📊 Team Analytics",
    "🥅 Goalies",
    "📈 Model Performance",
])


# ---------------------------
# TODAY'S PICKS
# ---------------------------
with tabs[0]:
    st.markdown(
        '<div class="section-label">DAILY NHL ANALYSIS</div>'
        '<div class="hero-title">Find Your Edge.</div>'
        '<p class="muted">Model-driven NHL moneyline probabilities '
        'and market comparisons.</p>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info(
            "No prediction report found. Add a file named "
            "nhl_fanduel_YYYY-MM-DD.csv inside the reports folder."
        )
    else:
        date_text = report_file.stem.replace("nhl_fanduel_", "")
        st.caption(f"Latest available report: {date_text}")

        edge_values = pd.to_numeric(
            df.get("edge_pp", pd.Series(dtype=float)),
            errors="coerce",
        )
        roi_values = pd.to_numeric(
            df.get("expected_roi_pct", pd.Series(dtype=float)),
            errors="coerce",
        )

        games = (
            df["matchup"].nunique()
            if "matchup" in df.columns
            else len(df) // 2
        )
        positive = int((edge_values > 0).sum())
        best_roi = roi_values.max() if not roi_values.empty else 0

        a, b, c, d = st.columns(4)
        with a:
            metric_card("GAMES ANALYZED", games)
        with b:
            metric_card("POSITIVE EDGES", positive, True)
        with c:
            metric_card("TEAM PREDICTIONS", len(df))
        with d:
            metric_card(
                "HIGHEST EST. ROI",
                f"{best_roi:+.2f}%" if pd.notna(best_roi) else "—",
                True,
            )

        st.markdown(
            '<div class="section-heading">Top Model Opportunities</div>',
            unsafe_allow_html=True,
        )
        st.caption("Ranked by estimated expected return.")

        ranked = df.copy()
        ranked["_roi"] = pd.to_numeric(
            ranked.get(
                "expected_roi_pct",
                pd.Series(0, index=ranked.index),
            ),
            errors="coerce",
        ).fillna(0)
        ranked = ranked.sort_values("_roi", ascending=False)

        only_positive = st.toggle(
            "Show only positive expected ROI", value=True
        )
        if only_positive:
            ranked = ranked[ranked["_roi"] > 0]

        if ranked.empty:
            st.info("No predictions match the current filter.")
        else:
            for _, row in ranked.iterrows():
                pick_card(row)

        with st.expander("View full prediction data"):
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

        st.download_button(
            "⬇ Download Prediction Report",
            data=df.to_csv(index=False),
            file_name=report_file.name,
            mime="text/csv",
        )


# ---------------------------
# TEAM ANALYTICS
# ---------------------------
with tabs[1]:
    st.markdown(
        '<div class="section-label">TEAM INTELLIGENCE</div>'
        '<div class="hero-title">Team Analytics.</div>',
        unsafe_allow_html=True,
    )
    st.caption("Compare model probabilities against market estimates.")

    if df.empty:
        st.info("Team analytics will appear once reports are available.")
    else:
        teams = sorted(df["team"].dropna().astype(str).unique())
        selected = st.selectbox("Select a team", teams)

        team_df = df[df["team"].astype(str) == selected]
        for _, row in team_df.iterrows():
            pick_card(row)

        if {
            "team", "model_win_pct", "no_vig_market_pct"
        }.issubset(df.columns):
            chart_df = df[
                ["team", "model_win_pct", "no_vig_market_pct"]
            ].copy()

            for col in ["model_win_pct", "no_vig_market_pct"]:
                chart_df[col] = pd.to_numeric(
                    chart_df[col], errors="coerce"
                )

            chart_df = chart_df.dropna()
            chart_df = chart_df.rename(columns={
                "model_win_pct": "Verse Model",
                "no_vig_market_pct": "Market (No Vig)",
            })
            chart_df = chart_df.set_index("team")

            st.markdown("#### Model vs. Market")
            st.bar_chart(chart_df)


# ---------------------------
# GOALIE ANALYTICS
# ---------------------------
with tabs[2]:
    st.markdown(
        '<div class="section-label">GOALTENDER INTELLIGENCE</div>'
        '<div class="hero-title">Goalie Analytics.</div>',
        unsafe_allow_html=True,
    )
    st.caption("Projected starters and their associated team forecasts.")

    if df.empty:
        st.info("Goalie information will appear with prediction data.")
    elif "projected_goalie" not in df.columns:
        st.info("The current report has no projected-goalie column.")
    else:
        goalie_cols = [
            col for col in [
                "team",
                "matchup",
                "projected_goalie",
                "goalie_win_pct",
                "model_win_pct",
                "fanduel_us_ml",
                "edge_pp",
            ]
            if col in df.columns
        ]

        goalie_df = df[goalie_cols].copy()
        goalie_df = goalie_df.rename(columns={
            "team": "Team",
            "matchup": "Matchup",
            "projected_goalie": "Projected Goalie",
            "goalie_win_pct": "Goalie Win %",
            "model_win_pct": "Model Win %",
            "fanduel_us_ml": "FanDuel Odds",
            "edge_pp": "Edge (pp)",
        })

        st.dataframe(
            goalie_df,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Projected starters may change. Goalie-related fields "
            "are shown as supplied by the prediction report."
        )


# ---------------------------
# MODEL PERFORMANCE
# ---------------------------
with tabs[3]:
    st.markdown(
        '<div class="section-label">MODEL TRACK RECORD</div>'
        '<div class="hero-title">Performance Center.</div>',
        unsafe_allow_html=True,
    )

    if history.empty:
        st.info(
            "Historical tracking isn't connected yet. "
            "Add history/predictions.csv to this repository "
            "to populate this section."
        )
    else:
        st.caption(
            "Historical prediction records from the connected CSV."
        )

        st.metric("Historical Records", len(history))

        # Show verified results only when a recognizable
        # settled-result column is available.
        result_col = next(
            (
                c for c in [
                    "result", "bet_result", "outcome",
                    "pick_result", "win"
                ]
                if c in history.columns
            ),
            None,
        )

        if result_col:
            raw = history[result_col].astype(str).str.lower().str.strip()
            wins = raw.isin(["win", "won", "w", "true", "1"])
            losses = raw.isin(["loss", "lost", "l", "false", "0"])
            settled = wins | losses

            if settled.any():
                n_wins = int(wins.sum())
                n_losses = int(losses.sum())
                win_rate = 100 * n_wins / (n_wins + n_losses)

                x, y, z = st.columns(3)
                x.metric("Settled Wins", n_wins)
                y.metric("Settled Losses", n_losses)
                z.metric("Win Rate", f"{win_rate:.1f}%")
            else:
                st.caption("No settled win/loss results recognized yet.")
        else:
            st.caption(
                "Result summaries will appear once the history "
                "file includes a recognized settled-result column."
            )

        st.markdown("#### Historical Predictions")
        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇ Download Historical Data",
            history.to_csv(index=False),
            file_name="verse_history.csv",
            mime="text/csv",
        )


# ---------------------------
# FOOTER
# ---------------------------
st.markdown("""
<div class="disclaimer">
    VERSE NHL INTELLIGENCE · Experimental analytics dashboard.
    Probabilities are not calibrated or guaranteed.
    Positive expected ROI is a model estimate, not proof
    of a profitable betting opportunity.
    Data may be stale and goalie projections may change.
</div>
""", unsafe_allow_html=True)
