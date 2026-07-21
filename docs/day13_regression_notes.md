# Day 13 Regression Notes

Day 13 focused on building the first MacroSense regression model.

The regression model estimates how much of a stock's weekly return can be explained by broad market returns, sector returns, and standardized macro shock variables.

The target variable is stock_return. The explanatory variables include market_return, sector_return, and macro z-score features such as change_10y_yield_zscore, change_vix_zscore, change_credit_spread_zscore, and change_oil_zscore.

The model uses ordinary least squares regression. OLS estimates coefficients that minimize the difference between actual stock returns and predicted stock returns.

A coefficient shows the estimated relationship between one explanatory variable and stock_return, holding the other variables constant. For example, a positive market_return coefficient means the stock tends to rise when the market rises. A negative change_vix_zscore coefficient means the stock tends to fall when volatility shocks increase.

R-squared measures how much of the variation in stock_return is explained by the model. A higher R-squared means the included market, sector, and macro variables explain more of the stock's historical weekly movements.

This regression does not prove causation. It provides a structured way to estimate historical sensitivity and prepare for residual attribution.