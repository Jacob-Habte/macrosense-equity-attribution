# Week 1 Summary: Project Foundation and Market Data Pipeline

## What was completed

During Week 1, I created the foundation for the MacroSense project and built the first working market data pipeline. The project folder, GitHub repo, README, requirements file, `.gitignore`, and main folder structure were created. I also set up the Python environment and installed the main data science packages needed for the project.

I built a reusable `get_stock_prices()` function that pulls historical stock price data for a given ticker using `yfinance`. The function returns a clean table with date, open, high, low, close, adjusted close, and volume.

I also built a `calculate_returns()` function that converts adjusted close prices into daily, weekly, or monthly returns. Weekly returns are the main default because they reduce daily noise while still providing enough observations for future regression analysis.

Finally, I added benchmark and sector ETF return functionality. The project can now pull weekly returns for broad market ETFs such as SPY and QQQ, along with sector ETFs such as XLK, XLF, XLE, XLY, XLI, XLV, XLP, XLU, and XLRE.

## Why this matters

MacroSense is designed to explain whether a stock moved because of company-specific factors, the broad market, its sector, or macroeconomic conditions. Before adding macroeconomic data or regression models, the project needs a reliable stock and benchmark return pipeline.

This Week 1 pipeline creates the foundation for the future attribution model. Stock returns can now be compared against market and sector returns, which will later help separate market-wide movement from sector-driven movement and unexplained company-specific movement.

## Key functions built

- `get_stock_prices(ticker, start_date, end_date)`
- `calculate_returns(price_df, frequency="weekly")`
- `get_benchmark_returns(start_date, end_date, frequency="weekly")`
- `get_sector_etf(ticker)`

## MVP tickers tested

- FICO
- AAPL
- JPM
- XOM

## Current limitations

The current sector ETF mapping is manual and only covers the MVP tickers. This is intentional for the first version of the project. Later, the project can be improved by automatically detecting sector ETFs using company metadata.

The data source is also free market data, which is useful for learning and project development but not institutional-grade.

## Week 1 result

By the end of Week 1, MacroSense has a working stock and ETF data pipeline. The project can pull stock prices, convert them into returns, pull benchmark and sector ETF returns, and prepare the data needed for future macro analysis and attribution modeling.