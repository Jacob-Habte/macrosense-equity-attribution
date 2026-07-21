# Day 10 Macro Feature Notes

Day 10 focused on converting raw macroeconomic levels into macro change features.

Raw macro levels show where an indicator is at a point in time. For example, the 10Y Treasury Yield level shows the current long-term interest rate. Macro changes show how much the indicator moved compared with the previous period.

This matters because markets often react to changes in expectations rather than only absolute levels. A 5% interest rate environment matters, but a move from 4.5% to 5.0% can be the event that changes valuation expectations.

For rate-like indicators such as the 10Y Treasury Yield, Fed Funds Rate, unemployment rate, mortgage rate, yield curve spread, and credit spreads, the project uses simple differences. These indicators are already measured as rates or spreads, so differences are easier to interpret.

For price-like or index-like indicators such as VIX, oil prices, CPI, and consumer sentiment, the project uses percent changes. This better captures the size of the move relative to the previous value.

These macro change features will later be used in regression to estimate how sensitive a stock’s returns are to changes in market fear, rates, credit stress, inflation, oil prices, and economic conditions.