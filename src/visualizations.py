import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_actual_vs_predicted(attribution_table):
    """
    Plot actual stock returns versus model-predicted returns over time.
    """

    data = attribution_table.copy()

    fig = px.line(
        data,
        x="date",
        y=["actual_return", "predicted_return"],
        title="Actual vs Predicted Weekly Returns",
        labels={
            "date": "Date",
            "value": "Weekly Return",
            "variable": "Return Type"
        }
    )

    return fig

def plot_residuals_over_time(attribution_table):
    """
    Plot residual returns over time.
    """

    data = attribution_table.copy()

    fig = px.bar(
        data,
        x="date",
        y="residual_return",
        title="Residual Return Over Time",
        labels={
            "date": "Date",
            "residual_return": "Residual Return"
        }
    )

    return fig

def plot_contribution_breakdown(attribution_table, row_index=-1):
    """
    Plot market, sector, macro, and residual contributions for one selected week.
    """

    row = attribution_table.iloc[row_index]

    contribution_data = {
        "driver": ["Market", "Sector", "Macro", "Residual"],
        "contribution": [
            row["market_contribution"],
            row["sector_contribution"],
            row["macro_contribution"],
            row["residual_return"]
        ]
    }

    fig = px.bar(
        contribution_data,
        x="driver",
        y="contribution",
        title="Return Attribution Breakdown",
        labels={
            "driver": "Driver",
            "contribution": "Return Contribution"
        }
    )

    

    return fig



def plot_largest_residuals(largest_residuals):
    """
    Plot the largest unexplained residual weeks.
    """

    data = largest_residuals.copy()

    fig = px.bar(
        data,
        x="date",
        y="residual_return",
        title="Largest Unexplained Residual Weeks",
        labels={
            "date": "Date",
            "residual_return": "Residual Return"
        }
    )

    return fig

def plot_coefficients(coefficient_table):
    """
    Plot regression coefficients.
    """

    data = coefficient_table.copy()

    # Remove the constant so the chart focuses on drivers.
    data = data[data["feature"] != "const"]

    fig = px.bar(
        data,
        x="coefficient",
        y="feature",
        orientation="h",
        title="Regression Coefficients",
        labels={
            "coefficient": "Coefficient",
            "feature": "Feature"
        }
    )

    return fig

def plot_return_contribution_waterfall(attribution_table, row_index=-1):
    """
    Create a waterfall chart showing how market, sector, macro,
    and residual contributions add up to actual return.
    """

    row = attribution_table.iloc[row_index]

    fig = go.Figure(
        go.Waterfall(
            name="Return Attribution",
            orientation="v",
            measure=[
                "relative",
                "relative",
                "relative",
                "relative",
                "total"
            ],
            x=[
                "Market",
                "Sector",
                "Macro",
                "Residual",
                "Actual Return"
            ],
            y=[
                row["market_contribution"],
                row["sector_contribution"],
                row["macro_contribution"],
                row["residual_return"],
                row["actual_return"]
            ],
            connector={"line": {"width": 1}}
        )
    )

    fig.update_layout(
        title="Return Attribution Waterfall",
        yaxis_title="Return Contribution",
        showlegend=False
    )

    return fig

def plot_macro_contributions(attribution_table, row_index=-1):
    """
    Plot individual macro contributions for a selected week.
    """

    row = attribution_table.iloc[row_index]

    macro_contribution_columns = [
        column for column in attribution_table.columns
        if column.endswith("_contribution")
        and column not in [
            "constant_contribution",
            "market_contribution",
            "sector_contribution",
            "macro_contribution",
            "total_explained_contribution"
        ]
    ]

    macro_data = []

    for column in macro_contribution_columns:
        macro_data.append(
            {
                "macro_factor": column.replace("_contribution", ""),
                "contribution": row[column]
            }
        )

    macro_df = pd.DataFrame(macro_data)

    macro_df = macro_df.sort_values(
        "contribution",
        key=lambda column: column.abs(),
        ascending=False
    )

    fig = px.bar(
        macro_df,
        x="contribution",
        y="macro_factor",
        orientation="h",
        title="Individual Macro Contributions",
        labels={
            "contribution": "Return Contribution",
            "macro_factor": "Macro Factor"
        }
    )

    return fig

def plot_cumulative_actual_vs_predicted(attribution_table):
    """
    Plot cumulative actual and predicted returns over time.
    """

    data = attribution_table.copy()

    data["cumulative_actual_return"] = (1 + data["actual_return"]).cumprod() - 1
    data["cumulative_predicted_return"] = (1 + data["predicted_return"]).cumprod() - 1

    fig = px.line(
        data,
        x="date",
        y=[
            "cumulative_actual_return",
            "cumulative_predicted_return"
        ],
        title="Cumulative Actual vs Predicted Returns",
        labels={
            "date": "Date",
            "value": "Cumulative Return",
            "variable": "Return Type"
        }
    )

    return fig