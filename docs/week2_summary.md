# Week 2 Summary

Week 2 expanded MacroSense from a market data pipeline into a working macro-aware attribution model.

## Completed Work

- Added FRED macroeconomic data through `src/macro_data.py`.
- Expanded the macro basket to include rates, inflation, labour market data, volatility, credit spreads, oil prices, consumer sentiment, mortgage rates, and yield curve spread.
- Built `src/data_pipeline.py` to merge stock returns, benchmark returns, sector returns, and macro indicators onto one weekly timeline.
- Created macro change features to measure how indicators moved week to week.
- Created z-score features to standardize macro shocks across different units.
- Built correlation analysis to rank relationships between stock returns and explanatory variables.
- Built an OLS regression model to estimate stock sensitivity to market, sector, and macro factors.
- Created an attribution table showing actual return, predicted return, market contribution, sector contribution, macro contribution, and residual return.
- Added readable MVP summary output to explain results in plain English.

## Current MVP Capability

The project can now take a supported ticker such as FICO, AAPL, MSFT, JPM, or XOM and produce a weekly attribution analysis.

The output can show whether a stock's movement was mostly explained by the broad market, its sector, macro shocks, or unexplained residual movement.

## Current Limitations

- Sector ETF mapping is still manual.
- The model uses historical relationships and does not prove causation.
- The current regression is a first-pass model and may be improved later with better feature selection.
- CSV outputs are saved locally and are not committed to GitHub.
- The model does not yet have a Streamlit dashboard.

## Next Steps

- Clean up code and notebooks.
- Add visualizations for attribution results.
- Build a simple Streamlit dashboard.
- Add ticker input.
- Add clearer case studies for FICO, JPM, and XOM.