# Day 14 Attribution Notes

Day 14 focused on turning the regression model into an attribution table.

The attribution table compares actual stock returns to predicted stock returns. The predicted return is calculated using the regression model's estimated coefficients and the weekly values of the explanatory variables.

The residual return is calculated as actual_return minus predicted_return. This residual represents the portion of the stock's weekly return that was not explained by market returns, sector returns, or macro shock variables.

The attribution table separates the predicted return into market contribution, sector contribution, macro contribution, and constant contribution. This makes the model easier to interpret because it shows whether the predicted return came mostly from broad market movement, sector movement, or macro conditions.

A large positive residual means the stock outperformed what the model expected. A large negative residual means the stock underperformed what the model expected. These residual weeks may reflect company-specific news, earnings surprises, investor sentiment, overreaction, or limitations in the model.

This step is central to MacroSense because it turns the project from a regression model into a usable stock movement attribution tool.