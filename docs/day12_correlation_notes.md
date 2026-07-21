# Day 12 Correlation Notes

Day 12 focused on calculating correlations between stock returns and possible explanatory variables.

Correlation measures how closely two variables move together. A positive correlation means two variables generally move in the same direction, while a negative correlation means they generally move in opposite directions. A correlation near zero means there is no clear linear relationship.

In MacroSense, the target variable is stock_return. The project compares stock_return against market_return, sector_return, and standardized macro shock variables such as change_vix_zscore, change_10y_yield_zscore, change_credit_spread_zscore, and change_oil_zscore.

This step is useful because it gives an early view of what factors appear most related to a stock's movement. For example, if sector_return has the highest correlation with stock_return, the stock may be strongly influenced by sector-level forces. If change_vix_zscore has a strong negative correlation, the stock may be sensitive to risk-off volatility shocks.

Correlation does not prove causation. It only shows historical co-movement. Later regression and residual analysis will provide a more structured attribution framework.