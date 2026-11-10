
import streamlit as st
import pandas as pd
from pathlib import Path
from html import escape

st.set_page_config(
    page_title="VERSE | NHL Intelligence",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# SETTINGS
# ==========================================

COVER_THRESHOLD = 65.0

# ==========================================
# STYLING
# ==========================================

st.html("""
<style>
.stApp {
    background: #090F1D;
    color: #F8FAFC;
}

.block-container {
    max-width: 1300px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3 {
    color: #F8FAFC;
}

.verse-title {
    font-size: 38px;
    font-weight: 900;
    letter-spacing: -1px;
}

.verse-title span {
    color: #4ADE80;
}

.verse-subtitle {
    color: #94A3B8;
    font-size: 12px;
    letter-spacing: 2px;
    margin-bottom: 25px;
}

.match-card {
    background: linear-gradient(
        135deg, #152238, #101B2C
    );
    border: 1px solid #293B54;
    border-radius: 18px;
    padding: 22px;
    margin: 18px 0;
}

.match-top {
    display: grid;
    grid-template-columns: 1fr 1.4fr 1fr;
    align-items: center;
    gap: 10px;
}

.team-name {
    font-size: 26px;
    font-weight: 850;
    color: #F8FAFC;
}

.team-prob {
    font-size: 22px;
    font-weight: 750;
    margin-top: 6px;
}

.small-label {
    color: #94A3B8;
    font-size: 10px;
    font-weight: 750;
    letter-spacing: 1px;
}

.projected-score {
    font-size: 32px;
    font-weight: 900;
    color: #F8FAFC;
    margin: 5px 0;
}

.lean-pill {
    display: inline-block;
    background: #123D30;
    border: 1px solid #28634D;
    color: #86EFAC;
    border-radius: 25px;
    padding: 6px 11px;
    font-size: 12px;
    font-weight: 750;
}

.neutral-pill {
    background: #334155;
    border-color: #475569;
    color: #E2E8F0;
}

.prob-bar {
    display: flex;
    width: 100%;
    height: 13px;
    border-radius: 20px;
    overflow: hidden;
    margin: 20px 0 10px;
    gap: 2px;
    background: #29374C;
}

.away-bar {
    background: #A9BDD6;
}

.home-bar {
    background: #4ADE80;
}

.section-label {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin: 20px 0 10px;
}

.market-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin: 12px 0;
}

.market-box {
    background: #17263C;
    border: 1px solid #34445C;
    border-radius: 12px;
    padding: 15px;
    min-width: 0;
}

.market-box.selected {
    background: #123D30;
    border: 1px solid #4ADE80;
}

.market-name {
    font-size: 14px;
    font-weight: 800;
    color: #F8FAFC;
}

.market-number {
    font-size: 25px;
    font-weight: 850;
    margin: 6px 0;
    color: #F8FAFC;
}

.selected .market-number {
    color: #86EFAC;
}

.market-detail {
    font-size: 12px;
    color: #94A3B8;
    line-height: 1.7;
}

.selected .market-detail {
    color: #BBF7D0;
}

.green-tag {
    color: #86EFAC;
    font-size: 11px;
    font-weight: 800;
    margin-top: 8px;
}

.guidance {
    background: #17263C;
    border: 1px solid #34445C;
    border-radius: 12px;
    padding: 15px;
    font-size: 13px;
    color: #E2E8F0;
    line-height: 1.7;
    margin: 15px 0;
}

.muted {
    color: #94A3B8;
    font-size: 12px;
    line-height: 1.6;
}

.disclaimer {
    border-top: 1px solid #293B54;
    margin-top: 35px;
    padding-top: 20px;
    color: #94A3B8;
    font-size: 11px;
}

@media(max-width:600px) {
    .match-card {
        padding: 14px;
    }

    .match-top {
        grid-template-columns: 1fr 1.2fr 1fr;
        gap: 5px;
    }

    .team-name {
        font-size: 20px;
    }

    .team-prob {
        font-size: 17px;
    }

    .projected-score {
        font-size: 25px;
    }

    .market-grid {
        gap: 8px;
    }

    .market-box {
        padding: 10px;
    }

    .market-number {
        font-size: 20px;
    }

    .lean-pill {
        font-size: 10px;
        padding: 5px 7px;
    }
}
</style>
""")

# ==========================================
# HELPERS
# ==========================================

def num(value, default=None):
    try:
        result = pd.to_numeric(value, errors="coerce")
        if pd.isna(result):
            return default
        return float(result)
    except (TypeError, ValueError):
        return default


def safe(value):
    if value is None:
        return "—"
    try:
        if pd.isna(value):
            return "—"
    except (TypeError, ValueError):
        pass
    return escape(str(value))


def fmt(value, decimals=1, suffix=""):
    value = num(value)
    if value is None:
        return "—"
    return f"{value:.{decimals}f}{suffix}"


def signed(value, suffix="%"):
    value = num(value)
    if value is None:
        return "—"
    return f"{value:+.1f}{suffix}"


def odds_fmt(value):
    value = num(value)
    if value is None:
        return "—"
    return f"+{value:.0f}" if value > 0 else f"{value:.0f}"


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


def puckline_data(team, row, sign):
    prefix = "plus" if sign > 0 else "minus"
    line = "+1.5" if sign > 0 else "-1.5"

    return {
        "team": team,
        "label": f"{team} {line}",
        "prob": num(
            row.get(f"puckline_{prefix}_1_5_prob_pct")
        ),
        "roi": num(
            row.get(f"puckline_{prefix}_1_5_roi_pct")
        ),
        "odds": num(
            row.get(f"puckline_{prefix}_1_5_odds")
        ),
    }


def market_tile(item, selected=False):
    css = "market-box selected" if selected else "market-box"

    prob = fmt(item["prob"], 1, "%")
    roi = signed(item["roi"])
    odds = odds_fmt(item["odds"])

    tag = (
        '<div class="green-tag">'
        '✓ QUALIFIED PUCK-LINE LEAN'
        '</div>'
        if selected else ""
    )

    return f"""
    <div class="{css}">
        <div class="market-name">{safe(item["label"])}</div>
        <div class="market-number">{prob}</div>
        <div class="market-detail">
            Estimated cover probability<br>
            FanDuel: {odds}<br>
            Estimated ROI: {roi}
        </div>
        {tag}
    </div>
    """


def moneyline_tile(team, row):
    prob = num(row.get("model_win_pct"))
    roi = num(row.get("expected_roi_pct"))
    edge = num(row.get("edge_pp"))

    roi_color = (
        "#86EFAC"
        if roi is not None and roi > 0
        else "#FDA4AF"
    )

    return f"""
    <div class="market-box">
        <div class="small-label">
            {safe(team)} MONEYLINE
        </div>
        <div class="market-number">
            {odds_fmt(row.get("fanduel_us_ml"))}
        </div>
        <div class="market-detail">
            Model win probability: {fmt(prob, 2, "%")}<br>
            Model edge: {signed(edge, " pp")}
        </div>
        <div style="color:{roi_color};
                    font-weight:800;
                    margin-top:8px;">
            {signed(roi)} estimated ROI
        </div>
    </div>
    """


# ==========================================
# MATCHUP CARD
# ==========================================

def render_matchup(group):
    if group.empty:
        return

    matchup = str(group.iloc[0].get("matchup", ""))

    if " @ " not in matchup:
        return

    away, home = [
        x.strip() for x in matchup.split(" @ ", 1)
    ]

    records = {
        str(row.get("team", "")): row
        for _, row in group.iterrows()
    }

    if away not in records or home not in records:
        return

    ar = records[away]
    hr = records[home]

    ap = num(ar.get("model_win_pct"))
    hp = num(hr.get("model_win_pct"))

    if ap is None or hp is None:
        st.warning(f"Missing probabilities: {matchup}")
        return

    ap = max(0, min(100, ap))
    hp = max(0, min(100, hp))

    # Favorite is based on model win probability.
    # Display only favorite -1.5 and underdog +1.5.

    if ap >= hp:
        favorite_team = away
        favorite_row = ar
        underdog_team = home
        underdog_row = hr
    else:
        favorite_team = home
        favorite_row = hr
        underdog_team = away
        underdog_row = ar

    underdog_line = puckline_data(
        underdog_team,
        underdog_row,
        +1,
    )

    favorite_line = puckline_data(
        favorite_team,
        favorite_row,
        -1,
    )

    lines = [underdog_line, favorite_line]

    # Qualify a puck line only if:
    # - Estimated cover probability >= 65%
    # - Estimated ROI > 0
    # - FanDuel odds are available

    qualified = [
        item for item in lines
        if item["prob"] is not None
        and item["prob"] >= COVER_THRESHOLD
        and item["roi"] is not None
        and item["roi"] > 0
        and item["odds"] is not None
    ]

    pick = (
        max(qualified, key=lambda x: x["roi"])
        if qualified else None
    )

    pick_label = pick["label"] if pick else None

    valid_lines = [
        item for item in lines
        if item["prob"] is not None
    ]

    cover_lean = (
        max(valid_lines, key=lambda x: x["prob"])
        if valid_lines else None
    )

    # Expected goals and projected score

    ag = num(ar.get("projected_goals"))
    hg = num(hr.get("projected_goals"))

    if ag is not None and hg is not None:
        projected_score = f"{round(ag)} – {round(hg)}"
        expected_goals = (
            f"{ag:.2f} – {hg:.2f} expected goals"
        )
    else:
        projected_score = "— – —"
        expected_goals = "Expected goals unavailable"

    if pick:
        lean_text = f"Lean: {pick['label']}"
        lean_class = "lean-pill"
    else:
        lean_text = "No qualifying puck-line lean"
        lean_class = "lean-pill neutral-pill"

    if pick:
        guidance = (
            f"{pick['label']} qualifies because Verse "
            f"estimates a {pick['prob']:.1f}% chance "
            f"of covering, meeting the "
            f"{COVER_THRESHOLD:.0f}% threshold, "
            f"with {pick['roi']:+.1f}% estimated ROI "
            f"at FanDuel odds {odds_fmt(pick['odds'])}."
        )
    else:
        guidance = (
            "No puck line qualifies. Verse requires "
            f"at least {COVER_THRESHOLD:.0f}% estimated "
            "cover probability AND positive estimated "
            "ROI at available FanDuel odds. "
            "Do not force a pick."
        )

    if cover_lean:
        likely_text = (
            f"{cover_lean['label']} "
            f"({cover_lean['prob']:.1f}%)"
        )
    else:
        likely_text = "Unavailable"

    # Best ROI across both moneylines and standard puck lines

    value_options = []

    for team, row in [(away, ar), (home, hr)]:
        roi = num(row.get("expected_roi_pct"))
        odds = num(row.get("fanduel_us_ml"))

        if roi is not None and odds is not None:
            value_options.append(
                (roi, f"{team} ML")
            )

    for item in lines:
        if (
            item["roi"] is not None
            and item["odds"] is not None
        ):
            value_options.append(
                (item["roi"], item["label"])
            )

    if value_options:
        best = max(
            value_options,
            key=lambda x: x[0],
        )

        best_value = (
            f"{best[1]} ({best[0]:+.1f}% est. ROI)"
            if best[0] > 0
            else "No positive estimated edge"
        )
    else:
        best_value = "Unavailable"

    html = f"""
    <div class="match-card">

        <div class="match-top">

            <div>
                <div class="small-label">AWAY</div>
                <div class="team-name">{safe(away)}</div>
                <div class="team-prob">{ap:.2f}%</div>
            </div>

            <div style="text-align:center;">
                <div class="small-label">
                    PROJECTED SCORE
                </div>
                <div class="projected-score">
                    {projected_score}
                </div>
                <div class="{lean_class}">
                    {safe(lean_text)}
                </div>
            </div>

            <div style="text-align:right;">
                <div class="small-label">HOME</div>
                <div class="team-name">{safe(home)}</div>
                <div class="team-prob">{hp:.2f}%</div>
            </div>

        </div>

        <div class="prob-bar">
            <div class="away-bar"
                 style="width:{ap:.2f}%;">
            </div>
            <div class="home-bar"
                 style="width:{hp:.2f}%;">
            </div>
        </div>

        <div class="muted" style="text-align:center;">
            {safe(expected_goals)} ·
            Rounded score illustration
        </div>

        <div class="section-label">
            PUCK LINE PROBABILITIES
        </div>

        <div class="muted">
            Underdog +1.5 and favorite -1.5 only.
            Green requires at least
            {COVER_THRESHOLD:.0f}% estimated cover
            probability and positive estimated ROI.
        </div>

        <div class="market-grid">
            {market_tile(
                underdog_line,
                pick_label == underdog_line["label"]
            )}
            {market_tile(
                favorite_line,
                pick_label == favorite_line["label"]
            )}
        </div>

        <div class="guidance">
            <strong>WHEN TO CONSIDER A PUCK LINE</strong>
            <div style="margin-top:7px;">
                {safe(guidance)}
            </div>
            <div class="muted" style="margin-top:8px;">
                Most likely to cover:
                {safe(likely_text)}
            </div>
        </div>

        <div class="muted" style="margin-bottom:12px;">
            Highest estimated ROI across ML and
            standard puck lines:
            <strong>{safe(best_value)}</strong>
        </div>

        <div class="section-label">
            MONEYLINE COMPARISON
        </div>

        <div class="market-grid">
            {moneyline_tile(away, ar)}
            {moneyline_tile(home, hr)}
        </div>

        <div class="section-label">
            PROJECTED GOALTENDERS
        </div>

        <div class="muted">
            {safe(away)}:
            {safe(ar.get("projected_goalie"))}
            &nbsp; · &nbsp;
            {safe(home)}:
            {safe(hr.get("projected_goalie"))}
        </div>

        <div class="muted" style="margin-top:15px;">
            Experimental projections. Model probabilities
            and ROI estimates have not yet been
            validated against historical results.
        </div>

    </div>
    """

    # Render HTML directly instead of Markdown.
    st.html(html)


# ==========================================
# LOAD DATA
# ==========================================

df, report_path = load_predictions()
history = load_history()

st.html(
    '<div class="verse-title">VERSE<span>.</span></div>'
    '<div class="verse-subtitle">'
    'NHL INTELLIGENCE · MONEYLINE + PUCK LINE'
    '</div>'
)

tabs = st.tabs([
    "Today's Picks",
    "Team Analytics",
    "Goalies",
    "Model Performance",
])

# ==========================================
# TAB 1: TODAY'S PICKS
# ==========================================

with tabs[0]:
    st.title("Today's Matchups")

    if df.empty:
        st.warning(
            "No prediction report found in reports/. "
            "Run the private model workflow first."
        )
    else:
        st.caption(
            f"Latest report: {report_path.name}"
        )

        matchups = (
            df["matchup"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        st.metric(
            "Matchups Analyzed",
            len(matchups),
        )

        for matchup in matchups:
            group = df[
                df["matchup"].astype(str) == matchup
            ]
            render_matchup(group)

# ==========================================
# TAB 2: TEAM ANALYTICS
# ==========================================

with tabs[1]:
    st.title("Team Analytics")

    if df.empty:
        st.info("No team data available.")
    else:
        options = sorted(
            df["matchup"]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_matchup = st.selectbox(
            "Choose a matchup",
            options,
        )

        window = st.select_slider(
            "Recent games",
            options=[5, 10, 20, 40],
            value=10,
        )

        pair = df[
            df["matchup"].astype(str)
            == selected_matchup
        ].copy()

        if len(pair) < 2:
            st.warning(
                "Both teams are required."
            )
        else:
            metrics = [
                ("xgf_per60", "Expected Goals For / 60"),
                ("xga_per60", "Expected Goals Against / 60"),
                ("xgf_pct", "Expected Goals Share (%)"),
                ("hdcf_pct", "High-Danger Chances (%)"),
                ("cf_pct", "Corsi For (%)"),
                (
                    "score_adj_xg_diff",
                    "Score-Adjusted xG Differential",
                ),
            ]

            rows = []

            for prefix, label in metrics:
                column = (
                    f"{prefix}_last_{window}"
                )

                record = {
                    "Metric": label
                }

                for _, team_row in pair.iterrows():
                    team = str(
                        team_row["team"]
                    )

                    record[team] = num(
                        team_row.get(column)
                    )

                rows.append(record)

            comparison = pd.DataFrame(rows)

            st.subheader(
                "Advanced Team Comparison"
            )

            st.dataframe(
                comparison,
                hide_index=True,
                use_container_width=True,
            )

            st.subheader(
                "Win Probability Comparison"
            )

            chart_data = pair[
                ["team", "model_win_pct"]
            ].copy()

            chart_data["model_win_pct"] = (
                pd.to_numeric(
                    chart_data["model_win_pct"],
                    errors="coerce",
                )
            )

            st.bar_chart(
                chart_data.set_index("team")
            )

            st.caption(
                "Advanced statistics are historical "
                "team metrics, not guaranteed future "
                "performance."
            )

# ==========================================
# TAB 3: GOALIE ANALYTICS
# ==========================================

with tabs[2]:
    st.title("Goalie Analytics")

    if df.empty:
        st.info(
            "No goalie data available."
        )
    else:
        goalie_columns = [
            "team",
            "matchup",
            "projected_goalie",
            "projected_goalie_status",
            "projected_goalie_confidence",
            "goalie_recent_sv_pct",
            "goalie_recent_shots",
            "goalie_games_checked",
            "goalie_win_pct_change",
        ]

        available = [
            c for c in goalie_columns
            if c in df.columns
        ]

        st.dataframe(
            df[available],
            hide_index=True,
            use_container_width=True,
        )

        teams = sorted(
            df["team"]
            .dropna()
            .astype(str)
            .unique()
        )

        team = st.selectbox(
            "Inspect a goalie",
            teams,
        )

        # Correctly define matching before use.
        matching = df[
            df["team"].astype(str) == team
        ]

        if not matching.empty:
            row = matching.iloc[0]

            st.subheader(
                safe(
                    row.get("projected_goalie")
                )
            )

            c1, c2, c3 = st.columns(3)

            sv = num(
                row.get("goalie_recent_sv_pct")
            )

            confidence = num(
                row.get("projected_goalie_confidence")
            )

            effect = num(
                row.get("goalie_win_pct_change")
            )

            c1.metric(
                "Recent Save %",
                f"{sv * 100:.2f}%"
                if sv is not None
                else "—",
            )

            c2.metric(
                "Usage Share",
                f"{confidence:.1f}%"
                if confidence is not None
                else "—",
            )

            c3.metric(
                "Win Probability Effect",
                f"{effect:+.2f} pp"
                if effect is not None
                else "—",
            )

            st.caption(
                "Projected starters are estimates, "
                "not confirmed starting goalies."
            )

# ==========================================
# TAB 4: MODEL PERFORMANCE
# ==========================================

with tabs[3]:
    st.title("Model Performance")

    if history.empty:
        st.info(
            "Historical predictions will appear "
            "when history/predictions.csv "
            "is available."
        )
    else:
        st.metric(
            "Historical Records",
            len(history),
        )

        result_col = next(
            (
                col for col in [
                    "result",
                    "bet_result",
                    "outcome",
                    "pick_result",
                    "win",
                ]
                if col in history.columns
            ),
            None,
        )

        if result_col:
            results = (
                history[result_col]
                .astype(str)
                .str.lower()
                .str.strip()
            )

            wins = results.isin([
                "win",
                "won",
                "w",
                "true",
                "1",
            ])

            losses = results.isin([
                "loss",
                "lost",
                "l",
                "false",
                "0",
            ])

            settled = wins | losses

            if settled.any():
                total = int(
                    settled.sum()
                )

                won = int(
                    wins.sum()
                )

                lost = int(
                    losses.sum()
                )

                a, b, c = st.columns(3)

                a.metric(
                    "Wins",
                    won,
                )

                b.metric(
                    "Losses",
                    lost,
                )

                c.metric(
                    "Win Rate",
                    f"{won / total * 100:.1f}%",
                )

        st.subheader(
            "Historical Predictions"
        )

        st.dataframe(
            history,
            hide_index=True,
            use_container_width=True,
        )

        st.download_button(
            "Download Historical Data",
            history.to_csv(index=False),
            file_name="verse_history.csv",
            mime="text/csv",
        )

# ==========================================
# FOOTER
# ==========================================

st.html("""
<div class="disclaimer">
    VERSE NHL INTELLIGENCE · Experimental
    analytics dashboard. The 65% threshold
    is a screening rule, not a validated
    winning strategy. Model probabilities,
    projected goals, and expected ROI are
    estimates, not guarantees.
</div>
""")
