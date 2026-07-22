import plotly.express as px


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