# MacroSense: Ticker-Agnostic Equity Movement Attribution Engine

MacroSense is a Python-based investment analysis project designed to help explain whether a stock’s recent movement was primarily driven by broad market trends, sector performance, macroeconomic conditions, or unexplained company-specific factors. The goal is to create a ticker-agnostic framework where a user can input a stock ticker and evaluate how much of the movement appears connected to market, sector, and macro drivers versus residual company-specific movement.

## MVP Features

The minimum viable product will include:

- Ticker input
- Stock data collection
- Macro data collection
- Sector mapping
- Weekly return calculation
- Regression-based attribution model
- Residual signal
- Streamlit dashboard

## Initial Test Tickers

The first sample tickers I plan to test later are:

- FICO — software/data/credit scoring exposure
- JPM — financials, interest rates, credit, and yield curve exposure
- XOM — energy, oil prices, inflation, and commodity cycle exposure

## Project Scope

This project focuses on explaining historical stock movement, not forecasting future stock prices. The model will estimate whether a stock’s return appears more connected to broad market performance, sector performance, macroeconomic changes, or unexplained residual movement. In the end, this model is focused on attribution NOT prediction.

The first version will prioritize interpretability over complexity. 

Goal is to create a clear and explainable investment analysis tool that can be discussed, and expanded over time.