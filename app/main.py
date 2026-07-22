import sys
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

# Add src folder to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.append(str(SRC_PATH))

from analysis import (
    run_full_mvp_analysis,
    summarize_attribution_row,
    create_summary_table
)

from market_data import get_ticker_profile, get_sector_etf

from visualizations import (
    plot_actual_vs_predicted,
    plot_residuals_over_time,
    plot_contribution_breakdown,
    plot_largest_residuals,
    plot_coefficients,
    plot_return_contribution_waterfall,
    plot_macro_contributions,
    plot_cumulative_actual_vs_predicted
)


st.set_page_config(
    page_title="MacroSense",
    layout="wide"
)


@st.cache_resource(show_spinner=False)
def cached_run_full_mvp_analysis(ticker, start_date, end_date):
    """
    Cache the full analysis so the app does not rerun expensive data pulls
    every time the dashboard refreshes.
    """

    return run_full_mvp_analysis(ticker, start_date, end_date)


st.title("MacroSense")
st.caption("Ticker-Agnostic Equity Movement Attribution Engine")

with st.expander("How to read this dashboard"):
    st.markdown(
        """
        **Actual return** is what the stock actually returned that week.

        **Predicted return** is what the regression model expected based on market returns,
        sector returns, and macro shock variables.

        **Market contribution** estimates how much broad market movement contributed.

        **Sector contribution** estimates how much the stock's sector ETF contributed.

        **Macro contribution** estimates the combined contribution from macro variables
        such as rates, VIX, oil, credit spreads, inflation, and unemployment.

        **Residual return** is the unexplained portion. A large residual may reflect
        company-specific news, earnings, sentiment, omitted variables, or model limitations.

        This project does not prove causation and should not be treated as investment advice.
        """
    )

st.markdown(
    """
    MacroSense estimates whether a stock's weekly movement was more closely linked to
    broad market returns, sector returns, macroeconomic shocks, or unexplained residual movement.
    """
)


with st.sidebar:
    st.header("Analysis Settings")

    ticker_input = st.text_input(
        "Enter ticker",
        value="FICO",
        help="Examples: FICO, AAPL, JPM, XOM, NVDA, COST, KO"
    )

    start_date_input = st.date_input(
        "Start date",
        value=date(2024, 1, 1)
    )

    end_date_input = st.date_input(
        "End date",
        value=date(2026, 1, 1)
    )

    run_button = st.button("Run MacroSense", use_container_width=True)

    st.divider()

    st.write("Current model uses:")
    st.write("- Weekly returns")
    st.write("- Market return")
    st.write("- Sector return")
    st.write("- Macro shock z-scores")
    st.write("- OLS regression")
    st.write("- Residual attribution")


# Validate dates before running anything.
if start_date_input >= end_date_input:
    st.sidebar.error("Start date must be before end date.")
    st.stop()


# Store the most recent successful input choices.
# This prevents the dashboard from disappearing when a user changes tabs/selectboxes.
if run_button:
    cleaned_ticker = ticker_input.upper().strip()

    if cleaned_ticker == "":
        st.error("Please enter a ticker.")
        st.stop()

    st.session_state["run_params"] = {
        "ticker": cleaned_ticker,
        "start_date": str(start_date_input),
        "end_date": str(end_date_input)
    }


if "run_params" not in st.session_state:
    st.warning("Enter a ticker in the sidebar and click Run MacroSense.")
    st.stop()


ticker = st.session_state["run_params"]["ticker"]
start_date = st.session_state["run_params"]["start_date"]
end_date = st.session_state["run_params"]["end_date"]


try:
    profile = get_ticker_profile(ticker)
    sector_etf = get_sector_etf(ticker)

    with st.spinner("Running MacroSense analysis..."):
        (
            merged_data,
            model,
            coefficient_table,
            attribution_table,
            largest_residuals,
            latest_summary,
            latest_summary_table
        ) = cached_run_full_mvp_analysis(
            ticker,
            start_date,
            end_date
        )

    # Make date columns safe for Streamlit date filtering/formatting.
    merged_data["date"] = pd.to_datetime(merged_data["date"])
    attribution_table["date"] = pd.to_datetime(attribution_table["date"])
    largest_residuals["date"] = pd.to_datetime(largest_residuals["date"])

    company_name = profile.get("long_name") or ticker
    sector_name = profile.get("sector") or "Unknown"
    industry_name = profile.get("industry") or "Unknown"

    st.subheader(f"{ticker} Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Company", company_name)
    col2.metric("Sector ETF", sector_etf)
    col3.metric("R-squared", round(model.rsquared, 3))
    col4.metric("Rows Used", merged_data.shape[0])

    if merged_data.shape[0] < 30:
        st.warning(
            "This ticker has fewer than 30 weekly observations in the selected date range. "
            "Regression results may be unstable."
        )

    if sector_etf == "SPY":
        st.info(
            "MacroSense used SPY as the sector proxy because a specific sector ETF could not be detected."
        )

    with st.expander("Ticker Profile"):
        st.write("Ticker:", ticker)
        st.write("Company:", company_name)
        st.write("Sector:", sector_name)
        st.write("Industry:", industry_name)
        st.write("Quote type:", profile.get("quote_type"))
        st.write("Currency:", profile.get("currency"))

    st.info(latest_summary["summary_text"])

    # Download buttons must come after the analysis is created.
    st.sidebar.divider()
    st.sidebar.subheader("Downloads")

    st.sidebar.download_button(
        label="Download attribution CSV",
        data=attribution_table.to_csv(index=False),
        file_name=f"{ticker}_attribution.csv",
        mime="text/csv"
    )

    st.sidebar.download_button(
        label="Download coefficients CSV",
        data=coefficient_table.to_csv(index=False),
        file_name=f"{ticker}_coefficients.csv",
        mime="text/csv"
    )

    st.sidebar.download_button(
        label="Download summary TXT",
        data=latest_summary["summary_text"],
        file_name=f"{ticker}_summary.txt",
        mime="text/plain"
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Executive Summary",
            "Attribution",
            "Residuals",
            "Regression",
            "Data"
        ]
    )

    with tab1:
        st.subheader("Latest Week Summary")

        st.dataframe(
            latest_summary_table,
            use_container_width=True
        )

        st.subheader("Actual vs Predicted Returns")

        st.plotly_chart(
            plot_actual_vs_predicted(attribution_table),
            use_container_width=True
        )

        st.subheader("Cumulative Actual vs Predicted Returns")

        st.plotly_chart(
            plot_cumulative_actual_vs_predicted(attribution_table),
            use_container_width=True
        )

    with tab2:
        st.subheader("Select a Week")

        week_options = attribution_table["date"].dt.strftime("%Y-%m-%d").tolist()

        selected_week = st.selectbox(
            "Week ending",
            week_options,
            index=len(week_options) - 1
        )

        selected_index = attribution_table[
            attribution_table["date"].dt.strftime("%Y-%m-%d") == selected_week
        ].index[0]

        selected_summary = summarize_attribution_row(
            ticker,
            attribution_table,
            model,
            row_index=selected_index
        )

        selected_summary_table = create_summary_table(selected_summary)

        st.write(selected_summary["summary_text"])

        st.dataframe(
            selected_summary_table,
            use_container_width=True
        )

        st.subheader("Contribution Breakdown")

        st.plotly_chart(
            plot_contribution_breakdown(
                attribution_table,
                row_index=selected_index
            ),
            use_container_width=True
        )

        st.plotly_chart(
            plot_return_contribution_waterfall(
                attribution_table,
                row_index=selected_index
            ),
            use_container_width=True
        )

        st.plotly_chart(
            plot_macro_contributions(
                attribution_table,
                row_index=selected_index
            ),
            use_container_width=True
        )

        st.subheader("Attribution Table")

        st.dataframe(
            attribution_table[
                [
                    "date",
                    "actual_return",
                    "predicted_return",
                    "market_contribution",
                    "sector_contribution",
                    "macro_contribution",
                    "residual_return"
                ]
            ],
            use_container_width=True
        )

    with tab3:
        st.subheader("Residuals Over Time")

        st.plotly_chart(
            plot_residuals_over_time(attribution_table),
            use_container_width=True
        )

        st.subheader("Largest Unexplained Residual Weeks")

        st.dataframe(
            largest_residuals[
                [
                    "date",
                    "actual_return",
                    "predicted_return",
                    "residual_return",
                    "absolute_residual"
                ]
            ],
            use_container_width=True
        )

        st.plotly_chart(
            plot_largest_residuals(largest_residuals),
            use_container_width=True
        )

    with tab4:
        st.subheader("Regression Coefficients")

        st.dataframe(
            coefficient_table,
            use_container_width=True
        )

        st.plotly_chart(
            plot_coefficients(coefficient_table),
            use_container_width=True
        )

        st.write(
            "Positive coefficients mean the stock return tends to move in the same direction as that factor. "
            "Negative coefficients mean the stock return tends to move in the opposite direction, holding other variables constant."
        )

    with tab5:
        st.subheader("Merged Dataset")

        st.dataframe(
            merged_data,
            use_container_width=True
        )

        st.subheader("Full Attribution Dataset")

        st.dataframe(
            attribution_table,
            use_container_width=True
        )

except Exception as error:
    st.error("MacroSense could not complete the analysis.")
    st.write("Error details:")
    st.code(str(error))
    st.write(
        "This may happen if the ticker is invalid, has missing data, does not have enough weekly observations, "
        "does not have usable sector metadata, or one of the source functions has not been saved/imported correctly."
    )