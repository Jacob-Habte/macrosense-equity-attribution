import sys
from pathlib import Path

import streamlit as st

# Add src folder to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.append(str(SRC_PATH))

from analysis import run_full_mvp_analysis
from visualizations import (
    plot_actual_vs_predicted,
    plot_residuals_over_time,
    plot_contribution_breakdown,
    plot_largest_residuals,
    plot_coefficients
)


st.set_page_config(
    page_title="MacroSense",
    layout="wide"
)

st.title("MacroSense: Equity Movement Attribution Engine")

st.write(
    "MacroSense estimates whether a stock's weekly movement was more closely "
    "linked to broad market returns, sector returns, macro shocks, or unexplained residual movement."
)

ticker = st.selectbox(
    "Choose a ticker",
    ["FICO", "AAPL", "MSFT", "JPM", "XOM"]
)

start_date = st.text_input("Start date", "2024-01-01")
end_date = st.text_input("End date", "2026-01-01")

run_button = st.button("Run analysis")

if run_button:
    with st.spinner("Running MacroSense analysis..."):

        (
            merged_data,
            model,
            coefficient_table,
            attribution_table,
            largest_residuals,
            latest_summary,
            latest_summary_table
        ) = run_full_mvp_analysis(
            ticker,
            start_date,
            end_date
        )

    st.subheader("Plain-English Summary")
    st.write(latest_summary["summary_text"])

    st.subheader("Model Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Ticker", ticker)
    col2.metric("R-squared", round(model.rsquared, 3))
    col3.metric("Rows Used", merged_data.shape[0])

    st.subheader("Latest Week Summary Table")
    st.dataframe(latest_summary_table)

    st.subheader("Actual vs Predicted Returns")
    st.plotly_chart(
        plot_actual_vs_predicted(attribution_table),
        use_container_width=True
    )

    st.subheader("Latest Week Contribution Breakdown")
    st.plotly_chart(
        plot_contribution_breakdown(attribution_table),
        use_container_width=True
    )

    st.subheader("Residuals Over Time")
    st.plotly_chart(
        plot_residuals_over_time(attribution_table),
        use_container_width=True
    )

    st.subheader("Largest Residual Weeks")
    st.dataframe(largest_residuals)
    st.plotly_chart(
        plot_largest_residuals(largest_residuals),
        use_container_width=True
    )

    st.subheader("Regression Coefficients")
    st.dataframe(coefficient_table)
    st.plotly_chart(
        plot_coefficients(coefficient_table),
        use_container_width=True
    )

    st.subheader("Full Attribution Table")
    st.dataframe(attribution_table)