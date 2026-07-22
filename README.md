# MacroSense: Equity Movement Attribution Engine

MacroSense is a Python-based equity movement attribution tool. It estimates whether a stock's weekly return was more closely linked to broad market returns, sector returns, macroeconomic shocks, or unexplained residual movement.

## Project Purpose

The goal is to combine market data, macroeconomic indicators, and regression analysis into a simple attribution framework.

The model does not prove causation and should not be treated as investment advice. It is a historical analysis tool designed to make stock movement explanations more structured and data-driven.

## Current Features

- Pulls stock price data using yfinance.
- Calculates daily, weekly, and monthly stock returns.
- Pulls market and sector ETF benchmark returns.
- Pulls macroeconomic data from FRED.
- Aligns stock, benchmark, sector, and macro data onto a weekly timeline.
- Creates macro change features.
- Standardizes macro shocks using z-scores.
- Runs correlation analysis.
- Runs OLS regression analysis.
- Creates attribution tables with actual return, predicted return, factor contributions, and residual return.
- Produces plain-English MVP summaries.
- Includes a Streamlit dashboard.

## MVP Tickers

The current MVP supports manual sector mapping for:

- FICO → XLK
- AAPL → XLK
- MSFT → XLK
- JPM → XLF
- XOM → XLE

## Project Structure

```text
app/              Streamlit dashboard
src/              Python source code
notebooks/        Testing notebook
docs/             Project notes and summaries
data/             Local data outputs
outputs/          Local dashboard/model outputs