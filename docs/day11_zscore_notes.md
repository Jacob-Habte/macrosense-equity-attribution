# Day 11 Z-Score Notes

Day 11 focused on standardizing macro change features using z-scores.

A z-score measures how unusual a value is compared with its own historical average. In this project, z-scores help identify whether a macro move was normal, large, or extreme.

This matters because different macro indicators are measured in different units. Interest rates and spreads are measured in percentage points, while oil, VIX, CPI, and consumer sentiment changes are measured as percent changes. Z-scores put these different variables onto a common scale.

A z-score near 0 means the macro move was close to normal. A z-score above 2 means the move was unusually large. A z-score below -2 means the move was unusually negative.

These standardized macro features will later help the project identify weeks where stock returns may have been influenced by unusual macro shocks, such as a spike in VIX, a jump in yields, a widening in credit spreads, or a sharp move in oil.