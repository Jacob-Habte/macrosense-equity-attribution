# Day 15 MVP Summary Notes

Day 15 focused on turning the MacroSense regression and attribution outputs into a readable MVP summary.

The project now takes a ticker, pulls stock data, pulls market and sector benchmark data, pulls macroeconomic data, aligns everything weekly, creates macro change features, standardizes macro shocks using z-scores, runs a regression model, builds an attribution table, identifies residuals, and generates a plain-English summary.

The MVP summary explains the selected stock's actual return, predicted return, market contribution, sector contribution, macro contribution, residual return, largest driver, top macro contributor, and model R-squared.

This matters because the goal of MacroSense is not only to calculate numbers, but to explain stock movement in business language. A user should be able to understand whether a stock's move was mostly linked to broad market movement, sector movement, macro conditions, or unexplained company-specific residual.

The summary does not prove causation and should not be treated as investment advice. It is a structured historical attribution framework.