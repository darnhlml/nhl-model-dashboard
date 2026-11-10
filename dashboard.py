
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

.verse-match-top {display:grid;grid-template-columns:1fr 1.2fr 1fr;gap:12px;align-items:center;}
.verse-center-label {text-align:center;}
.verse-team-prob {font-size:25px;font-weight:800;color:#F8FAFC;margin-top:7px;}
.verse-dual-track {display:flex;width:100%;height:13px;border-radius:99px;overflow:hidden;gap:3px;background:#29374C;margin:18px 0 22px;}
.verse-away-fill {background:linear-gradient(90deg,#7B91B3,#A9BDD6);}
.verse-home-fill {background:linear-gradient(90deg,#22C55E,#86EFAC);}
.verse-two-markets {display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.verse-market {background:#101A2B;border:1px solid #293B54;border-radius:12px;padding:15px;}
.verse-market-price {font-size:24px;font-weight:800;color:#F8FAFC;margin:7px 0;}
.verse-market-heading {color:#E2E8F0;font-size:12px;font-weight:800;letter-spacing:1.3px;margin:20px 0 10px;}
.verse-spreads {display:grid;grid-template-columns:1fr 1fr;gap:9px;}
.verse-spread-row {background:#101A2B;border:1px solid #293B54;border-radius:10px;padding:12px;display:flex;justify-content:space-between;gap:12px;color:#E2E8F0;font-size:13px;}
.verse-spread-row strong {color:#94A3B8;}
@media (max-width:600px) {
 .verse-match-top {grid-template-columns:1fr .8fr 1fr;gap:5px;}
 .verse-center-label .stat-label {font-size:8px;}
 .verse-team-prob {font-size:20px;}
 .verse-two-markets,.verse-spreads {grid-template-columns:1fr 1fr;gap:7px;}
 .verse-market {padding:10px;}
 .verse-market-price {font-size:19px;}
 .verse-spread-row {flex-direction:column;padding:9px;gap:4px;}
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


def matchup_card(group):
    '''One matchup card, both teams, without inventing puck-line odds.'''
    if group.empty:
        return
    matchup = str(group.iloc[0].get("matchup", ""))
    if " @ " not in matchup:
        return
    away, home = [x.strip() for x in matchup.split(" @ ", 1)]
    records = {str(r.get("team", "")): r for _, r in group.iterrows()}
    if away not in records or home not in records:
        return
    ar, hr = records[away], records[home]
    ap = numeric(ar.get("model_win_pct"), None)
    hp = numeric(hr.get("model_win_pct"), None)
    if ap is None or hp is None:
        st.warning(f"Missing probabilities for {matchup}")
        return
    ap = max(0, min(100, ap))
    hp = max(0, min(100, hp))
    favorite = away if ap > hp else home if hp > ap else "Even"
    aroi = numeric(ar.get("expected_roi_pct"), None)
    hroi = numeric(hr.get("expected_roi_pct"), None)
    aedge = numeric(ar.get("edge_pp"), None)
    hedge = numeric(hr.get("edge_pp"), None)

    def signed(v, suffix="%"):
        return f"{v:+.2f}{suffix}" if v is not None else "—"

    def roi_class(v):
        return "green-text" if v is not None and v > 0 else "red-text" if v is not None and v < 0 else ""

    def spread_row(team, row, sign):
        prefix = 'plus' if sign > 0 else 'minus'
        odds = row.get(f'puckline_{prefix}_1_5_odds')
        probability = numeric(row.get(f'puckline_{prefix}_1_5_prob_pct'), None)
        value = numeric(row.get(f'puckline_{prefix}_1_5_roi_pct'), None)
        label = f'{team} {"+" if sign > 0 else "-"}1.5'
        odds_text = odds_label(odds)
        details = f'{probability:.1f}% cover' if probability is not None else 'Awaiting model'
        if value is not None:
            details += f' · {value:+.1f}% est. ROI'
        return f'<div class="verse-spread-row"><span>{escape(label)}<div class="muted">{escape(details)}</div></span><strong>{escape(odds_text)}</strong></div>'

    ag = numeric(ar.get('projected_goals'), None)
    hg = numeric(hr.get('projected_goals'), None)
    projected = (f'{ag:.2f} – {hg:.2f} expected goals' if ag is not None and hg is not None
                 else 'Awaiting scoring model')
    options = []
    for team, row in ((away, ar), (home, hr)):
        for sign in (1, -1):
            p = numeric(row.get(f'puckline_{"plus" if sign > 0 else "minus"}_1_5_prob_pct'), None)
            r = numeric(row.get(f'puckline_{"plus" if sign > 0 else "minus"}_1_5_roi_pct'), None)
            if p is not None:
                options.append((p, r, f'{team} {"+" if sign > 0 else "-"}1.5'))
    cover_lean = max(options, key=lambda x: x[0])[2] if options else 'Unavailable'
    value_options = [(r, label) for p, r, label in options if r is not None]
    value_options += [(v, f'{team} ML') for team, v in ((away, aroi), (home, hroi)) if v is not None]
    best_value = max(value_options) if value_options else None
    value_lean = (best_value[1] if best_value and best_value[0] > 0 else 'No positive estimated edge')

    def team_market(team, row, probability, roi, edge):
        return f"""<div class="verse-market">
            <div class="stat-label">{escape(team)} MONEYLINE</div>
            <div class="verse-market-price">{odds_label(row.get("fanduel_us_ml"))}</div>
            <div class="muted">Model: {probability:.2f}% · Edge: {signed(edge, " pp")}</div>
            <div class="{roi_class(roi)}" style="font-weight:800;margin-top:5px;">
                {signed(roi)} estimated ROI
            </div>
        </div>"""

    st.markdown(f"""
    <div class="pick-card verse-match-card">
        <div class="verse-match-top">
            <div class="verse-team-side">
                <div class="stat-label">AWAY</div>
                <div class="team-name">{escape(away)}</div>
                <div class="verse-team-prob">{ap:.2f}%</div>
            </div>
            <div class="verse-center-label">
                <div class="stat-label">MODEL WIN PROBABILITY</div>
                <div class="muted">{escape(favorite)} {"favoured" if favorite != "Even" else "matchup"}</div>
            </div>
            <div class="verse-team-side" style="text-align:right;">
                <div class="stat-label">HOME</div>
                <div class="team-name">{escape(home)}</div>
                <div class="verse-team-prob">{hp:.2f}%</div>
            </div>
        </div>
        <div class="verse-dual-track">
            <div class="verse-away-fill" style="width:{ap:.2f}%;"></div>
            <div class="verse-home-fill" style="width:{hp:.2f}%;"></div>
        </div>
        <div style="text-align:center;background:#101A2B;border:1px solid #293B54;border-radius:12px;padding:14px;margin:14px 0;">
            <div class="stat-label">PROJECTED SCORING · EXPERIMENTAL</div>
            <div style="font-weight:800;color:#F8FAFC;font-size:20px;">{escape(projected)}</div>
            <div class="muted">Most likely puck-line cover: {escape(cover_lean)}</div>
            <div class="muted">Highest estimated ROI: {escape(value_lean)}</div>
        </div>
        <div class="verse-two-markets">
            {team_market(away, ar, ap, aroi, aedge)}
            {team_market(home, hr, hp, hroi, hedge)}
        </div>
        <div class="verse-market-heading">PUCK LINES · ±1.5 GOALS</div>
        <div class="verse-spreads">
            {spread_row(away, ar, +1)}
            {spread_row(home, hr, -1)}
            {spread_row(home, hr, +1)}
            {spread_row(away, ar, -1)}
        </div>
        <div class="goalie-line">🥅 {escape(away)}: {txt(ar.get("projected_goalie"))} &nbsp; · &nbsp;
        {escape(home)}: {txt(hr.get("projected_goalie"))}</div>
        <div class="muted" style="margin-top:9px;">Goal-margin and puck-line probabilities use an unvalidated scoring model; projected goals are averages, not a predicted exact score. Positive estimated ROI is not proven value.</div>
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
        st.caption("Matchups ranked by the highest estimated moneyline ROI. Both teams shown; puck-line probabilities and odds appear when supplied by the V3 model.")

        ranked = df.copy()
        ranked["_roi"] = pd.to_numeric(
            ranked.get(
                "expected_roi_pct",
                pd.Series(0, index=ranked.index),
            ),
            errors="coerce",
        ).fillna(0)
        # Group both teams into a single matchup card; rank by best team ROI.
        ranked = ranked.sort_values("_roi", ascending=False)

        only_positive = st.toggle(
            "Show only positive expected ROI", value=True
        )
        if only_positive:
            qualifying = ranked.loc[ranked["_roi"] > 0, "matchup"].unique()
            ranked = ranked[ranked["matchup"].isin(qualifying)]

        if ranked.empty:
            st.info("No matchups match the current filter.")
        else:
            for _, matchup_group in ranked.groupby("matchup", sort=False):
                matchup_card(matchup_group)

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
# ADVANCED TEAM ANALYTICS
# ---------------------------
with tabs[1]:
    st.markdown(
        '<div class="section-label">TEAM INTELLIGENCE</div>'
        '<div class="hero-title">Advanced Matchup Lab.</div>',
        unsafe_allow_html=True,
    )
    st.caption("5v5 advanced statistics from the latest report. These metrics provide context; they are not yet additional inputs to Verse's win probabilities.")

    if df.empty or "matchup" not in df.columns or "team" not in df.columns:
        st.info("Advanced team analytics will appear when a prediction report is available.")
    else:
        matchup_options = sorted(df["matchup"].dropna().astype(str).unique())
        matchup = st.selectbox("Choose a matchup", matchup_options, key="analytics_matchup")
        window = st.segmented_control("Recent games", options=[5, 10, 20, 40], default=10, key="analytics_window")
        window = int(window or 10)
        pair = df[df["matchup"].astype(str) == matchup].copy()
        if len(pair) < 2:
            st.warning("Both teams must be present in the report to compare this matchup.")
        else:
            away_rows = pair[pair["side"].astype(str).str.upper() == "AWAY"]
            home_rows = pair[pair["side"].astype(str).str.upper() == "HOME"]
            if away_rows.empty or home_rows.empty:
                st.warning("The matchup is missing a HOME or AWAY row.")
            else:
                away = away_rows.iloc[0]
                home = home_rows.iloc[0]
                away_name, home_name = str(away["team"]), str(home["team"])
                st.markdown(f"### {escape(away_name)} @ {escape(home_name)}")

                def advanced_value(row, prefix):
                    col = f"{prefix}_last_{window}"
                    return numeric(row.get(col), None)

                def advanced_label(value, suffix="", decimals=2):
                    return "—" if value is None else f"{value:.{decimals}f}{suffix}"

                st.markdown("#### Offensive and Defensive Production")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**{away_name} · Away**")
                    st.metric("Expected Goals For / 60", advanced_label(advanced_value(away, "xgf_per60")))
                    st.metric("Expected Goals Against / 60", advanced_label(advanced_value(away, "xga_per60")))
                    st.metric("Expected Goals Share", advanced_label(advanced_value(away, "xgf_pct"), "%"))
                with c2:
                    st.markdown(f"**{home_name} · Home**")
                    st.metric("Expected Goals For / 60", advanced_label(advanced_value(home, "xgf_per60")))
                    st.metric("Expected Goals Against / 60", advanced_label(advanced_value(home, "xga_per60")))
                    st.metric("Expected Goals Share", advanced_label(advanced_value(home, "xgf_pct"), "%"))

                metric_definitions = [
                    ("xgf_pct", "Expected Goals Share (%)", "Higher is generally better"),
                    ("hdcf_pct", "High-Danger Chance Share (%)", "Higher is generally better"),
                    ("cf_pct", "Corsi For (%)", "Higher is generally better"),
                    ("xgf_per60", "Expected Goals For / 60", "Higher is generally better"),
                    ("xga_per60", "Expected Goals Against / 60", "Lower is generally better"),
                    ("score_adj_xg_diff", "Score-Adjusted xG Differential", "Higher is generally better"),
                ]
                records = []
                for key, label, interpretation in metric_definitions:
                    records.append({
                        "Metric": label,
                        away_name: advanced_value(away, key),
                        home_name: advanced_value(home, key),
                        "Interpretation": interpretation,
                    })
                comparison = pd.DataFrame(records)
                st.markdown("#### Advanced Head-to-Head Comparison")
                st.dataframe(comparison, hide_index=True, use_container_width=True)

                for key, title, _ in metric_definitions:
                    values = {away_name: advanced_value(away, key), home_name: advanced_value(home, key)}
                    values = {name: value for name, value in values.items() if value is not None}
                    if values:
                        st.markdown(f"**{title}**")
                        st.bar_chart(pd.DataFrame({"Value": values}).rename_axis("Team"), horizontal=True)

                st.markdown("#### Model vs. Market")
                forecast = pd.DataFrame({
                    "Team": [away_name, home_name],
                    "Verse Model": [numeric(away.get("model_win_pct"), None), numeric(home.get("model_win_pct"), None)],
                    "Market (No Vig)": [numeric(away.get("no_vig_market_pct"), None), numeric(home.get("no_vig_market_pct"), None)],
                }).set_index("Team")
                st.bar_chart(forecast)
                st.caption("These are team-level 5v5 statistics, not opponent-adjusted matchup forecasts. Goalie and special-teams effects are not included in the comparison charts.")


# ---------------------------
# GOALIE ANALYTICS
# ---------------------------
with tabs[2]:
    st.markdown(
        '<div class="section-label">GOALTENDER INTELLIGENCE</div>'
        '<div class="hero-title">Goalie Analytics.</div>',
        unsafe_allow_html=True,
    )
    st.caption("Projected starters based on historical usage; no confirmed-starter claims. Recent save percentage is not GSAx.")

    if df.empty:
        st.info("Goalie information will appear with prediction data.")
    elif "projected_goalie" not in df.columns:
        st.info("The current report has no projected-goalie column.")
    else:
        goalie_columns = {
            "team": "Team",
            "matchup": "Matchup",
            "projected_goalie": "Projected Goalie",
            "projected_goalie_status": "Projection Status",
            "projected_goalie_confidence": "Usage Share (%)",
            "goalie_recent_sv_pct": "Recent SV%",
            "goalie_recent_shots": "Recent Shots",
            "goalie_games_checked": "Games Checked",
            "goalie_win_pct_change": "Goalie Effect (pp)",
            "model_win_pct": "Model Win (%)",
            "fanduel_us_ml": "FanDuel Odds",
        }
        available = [col for col in goalie_columns if col in df.columns]
        goalie_df = df[available].copy().rename(columns=goalie_columns)
        st.dataframe(goalie_df, hide_index=True, use_container_width=True)

        if "team" in df.columns:
            chosen = st.selectbox("Inspect a goalie projection", sorted(df["team"].dropna().astype(str).unique()), key="goalie_team")
            matching = df[df["team"].astype(str) == chosen]
            if not matching.empty:
                player = matching.iloc[0]
                st.markdown(f"### {txt(player.get('projected_goalie'))} · {escape(chosen)}")
                g1, g2, g3 = st.columns(3)
                with g1:
                    sv = numeric(player.get("goalie_recent_sv_pct"), None)
                    st.metric("Recent Save %", f"{sv * 100:.2f}%" if sv is not None else "—")
                with g2:
                    share = numeric(player.get("projected_goalie_confidence"), None)
                    st.metric("Recent Usage Share", f"{share:.1f}%" if share is not None else "—")
                with g3:
                    change = numeric(player.get("goalie_win_pct_change"), None)
                    st.metric("Model Probability Change", f"{change:+.2f} pp" if change is not None else "—")
                st.caption("Usage share is a heuristic, not a calibrated probability that this goalie starts. The model's goalie adjustment is experimental.")


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
