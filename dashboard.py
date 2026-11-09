
import math
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NHL Moneyline Model",
    page_icon="🏒",
    layout="wide"
)

REPORTS = Path("reports")
HISTORY = Path("history/predictions.csv")


def read_csv(path):
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except (OSError, pd.errors.EmptyDataError):
        return pd.DataFrame()


@st.cache_data(ttl=60)
def load_data():
    files = sorted(REPORTS.glob("nhl_fanduel_*.csv"))
    latest = read_csv(files[-1]) if files else pd.DataFrame()
    history = read_csv(HISTORY)
    return latest, history


def numeric(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def percent(value, digits=1):
    if pd.isna(value):
        return "N/A"
    return f"{value:.{digits}f}%"


def metric(label, value):
    st.metric(label, value)


def performance_table(df):
    required = {"model_win_pct", "won"}
    if df.empty or not required.issubset(df.columns):
        return pd.DataFrame()

    data = df.copy()
    data = numeric(data, [
        "model_win_pct", "won", "fanduel_us_ml"
    ])
    data = data.dropna(subset=["model_win_pct", "won"])
    data = data[data["won"].isin([0, 1])]

    if data.empty:
        return data

    data["probability"] = (
        data["model_win_pct"] / 100
    ).clip(0.000001, 0.999999)

    data["correct"] = (
        (data["probability"] >= 0.5).astype(int)
        == data["won"].astype(int)
    )

    data["brier"] = (
        data["probability"] - data["won"]
    ) ** 2

    data["log_loss"] = -(
        data["won"] * data["probability"].map(math.log)
        + (1 - data["won"])
        * (1 - data["probability"]).map(math.log)
    )

    return data


st.title("🏒 NHL Moneyline Model")
st.caption(
    "Experimental NHL predictions • "
    "Not a validated betting system"
)

latest, history = load_data()

if latest.empty and history.empty:
    st.warning(
        "No predictions found yet. Run the GitHub Actions "
        "workflow and make sure the CSV files are available."
    )
    st.stop()

page = st.sidebar.radio(
    "Dashboard",
    [
        "Daily Predictions",
        "Team & Goalie Analytics",
        "Model Performance"
    ]
)

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

if page == "Daily Predictions":
    st.header("Daily Predictions")

    if latest.empty:
        st.info("No daily report available.")
        st.stop()

    df = latest.copy()
    df = numeric(df, [
        "model_win_pct", "edge_pp",
        "expected_roi_pct", "goalie_recent_sv_pct",
        "goalie_win_pct_change"
    ])

    report_date = (
        str(df["date"].iloc[0])
        if "date" in df.columns else "Latest"
    )
    st.caption(f"Report date: {report_date}")

    games = (
        df["matchup"].nunique()
        if "matchup" in df.columns else 0
    )

    positive = (
        int((df["edge_pp"] > 0).sum())
        if "edge_pp" in df.columns else 0
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        metric("Games", games)
    with c2:
        metric("Positive edges", positive)
    with c3:
        metric("Team predictions", len(df))

    st.subheader("All predictions")

    columns = [
        "matchup", "team", "side",
        "model_win_pct", "fanduel_us_ml",
        "no_vig_market_pct", "edge_pp",
        "expected_roi_pct", "projected_goalie",
        "goalie_win_pct_change"
    ]

    available = [c for c in columns if c in df.columns]

    if "expected_roi_pct" in df.columns:
        df = df.sort_values(
            "expected_roi_pct", ascending=False
        )

    st.dataframe(
        df[available],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Positive model edge is not proof of a profitable bet. "
        "The probabilities are not yet calibrated."
    )

    st.download_button(
        "Download daily predictions CSV",
        data=latest.to_csv(index=False),
        file_name=f"nhl_predictions_{report_date}.csv",
        mime="text/csv"
    )


elif page == "Team & Goalie Analytics":
    st.header("Team & Goalie Analytics")

    if latest.empty:
        st.info("No daily report available.")
        st.stop()

    df = latest.copy()

    if "team" not in df.columns:
        st.warning("Team column missing.")
        st.stop()

    team = st.selectbox(
        "Select a team",
        sorted(df["team"].dropna().unique())
    )

    row = df[df["team"] == team].iloc[0]

    st.subheader(f"{team} — Current matchup")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Model win probability",
            percent(pd.to_numeric(
                row.get("model_win_pct"), errors="coerce"
            ))
        )

    with c2:
        st.metric(
            "Projected goalie",
            str(row.get("projected_goalie", "Unknown"))
        )

    with c3:
        sv = pd.to_numeric(
            row.get("goalie_recent_sv_pct"),
            errors="coerce"
        )
        st.metric(
            "Recent goalie SV%",
            percent(sv * 100, 2)
        )

    st.subheader("Recent 5v5 xG differential")

    form = {}
    for n in (5, 10, 20, 40):
        val = pd.to_numeric(
            row.get(f"xg_diff_last_{n}"),
            errors="coerce"
        )
        if pd.notna(val):
            form[f"Last {n}"] = val

    if form:
        st.bar_chart(
            pd.DataFrame.from_dict(
                form, orient="index", columns=["xG diff"]
            )
        )

    st.subheader("Goalie projection details")

    fields = [
        "projected_goalie",
        "projected_goalie_status",
        "projected_goalie_confidence",
        "goalie_games_checked",
        "goalie_recent_sv_pct",
        "goalie_recent_shots",
        "goalie_recent_saves",
        "goalie_win_pct_change",
        "goalie_adjustment_method"
    ]

    details = {
        field: row[field]
        for field in fields if field in row.index
    }

    st.dataframe(
        pd.DataFrame(
            details.items(), columns=["Metric", "Value"]
        ),
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Projected-goalie confidence is a usage score, "
        "not a calibrated probability of starting."
    )


else:
    st.header("Historical Model Performance")

    if history.empty:
        st.info(
            "No historical predictions yet. They will be "
            "collected automatically after the workflow runs."
        )
        st.stop()

    st.subheader("Prediction archive")

    st.metric("Saved team predictions", len(history))

    if "date" in history.columns:
        st.metric(
            "Dates tracked",
            history["date"].nunique()
        )

    results = performance_table(history)

    if results.empty:
        st.info(
            "No completed game results have been recorded yet. "
            "Performance metrics will appear after games finish."
        )
    else:
        # Each game has two team predictions.
        # These metrics measure prediction quality per team.
        accuracy = results["correct"].mean() * 100
        brier = results["brier"].mean()
        logloss = results["log_loss"].mean()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Prediction accuracy", f"{accuracy:.1f}%")
        with c2:
            st.metric("Brier score", f"{brier:.4f}")
        with c3:
            st.metric("Log loss", f"{logloss:.4f}")

        st.caption(
            "Lower Brier score and log loss are better. "
            "Accuracy alone does not measure calibration."
        )

        st.subheader("Probability calibration")

        results = results.copy()
        results["probability_bucket"] = pd.cut(
            results["probability"],
            bins=[0, .2, .4, .6, .8, 1],
            include_lowest=True
        )

        calibration = (
            results.groupby(
                "probability_bucket", observed=True
            )
            .agg(
                predicted=("probability", "mean"),
                actual=("won", "mean"),
                count=("won", "size")
            )
            .reset_index()
        )

        calibration["predicted"] *= 100
        calibration["actual"] *= 100
        calibration["bucket"] = (
            calibration["probability_bucket"].astype(str)
        )

        st.line_chart(
            calibration.set_index("bucket")[
                ["predicted", "actual"]
            ]
        )

        st.dataframe(
            calibration[
                ["bucket", "predicted", "actual", "count"]
            ],
            hide_index=True,
            use_container_width=True
        )

        st.subheader("Illustrative flat-stake returns")

        if "fanduel_us_ml" in results.columns:
            bets = results.dropna(
                subset=["fanduel_us_ml"]
            ).copy()

            # Only one side per game, selected using
            # the archived model's positive expected ROI.
            if "expected_roi_pct" in bets.columns:
                bets["expected_roi_pct"] = pd.to_numeric(
                    bets["expected_roi_pct"],
                    errors="coerce"
                )
                bets = bets[
                    bets["expected_roi_pct"] > 0
                ].copy()

            if not bets.empty:
                odds = bets["fanduel_us_ml"]
                profit_if_win = odds.apply(
                    lambda o: (
                        100 / abs(o) if o < 0
                        else o / 100
                    )
                )

                bets["unit_return"] = (
                    bets["won"] * profit_if_win
                    - (1 - bets["won"])
                )

                bets = bets.sort_values(
                    ["date", "matchup"]
                )

                bets["cumulative_units"] = (
                    bets["unit_return"].cumsum()
                )

                st.metric(
                    "Simulated flat-stake ROI",
                    f"{bets['unit_return'].mean() * 100:.2f}%"
                )

                st.line_chart(
                    bets.reset_index(drop=True)[
                        "cumulative_units"
                    ]
                )

                st.caption(
                    "Historical simulation only. Uses saved "
                    "odds, assumes each positive-ROI selection "
                    "could be placed at that price, and excludes "
                    "fees, limits and execution effects."
                )

    st.subheader("Historical records")

    columns = [
        "date", "matchup", "team",
        "model_win_pct", "fanduel_us_ml",
        "expected_roi_pct", "projected_goalie",
        "won", "game_status"
    ]

    available = [
        c for c in columns if c in history.columns
    ]

    st.dataframe(
        history[available].sort_values(
            "date", ascending=False
        ) if "date" in history.columns else history[available],
        hide_index=True,
        use_container_width=True
    )
