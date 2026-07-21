import pandas as pd
import statsmodels.api as sm

from data_pipeline import merge_stock_macro_data

REGRESSION_FEATURES = [
    "market_return",
    "sector_return",
    "change_10y_yield_zscore",
    "change_fed_funds_rate_zscore",
    "change_yield_curve_spread_zscore",
    "change_unemployment_rate_zscore",
    "change_credit_spread_zscore",
    "change_mortgage_rate_zscore",
    "change_vix_zscore",
    "change_oil_zscore",
    "change_cpi_zscore",
    "change_consumer_sentiment_zscore"
]

def format_percent(value):
    """
    Convert a decimal return into a readable percent string.

    Example:
        0.052 becomes '5.20%'
        -0.031 becomes '-3.10%'
    """

    return f"{value * 100:.2f}%"

def calculate_correlations(df, target_column="stock_return"):
    """
    Calculate correlations between stock returns and key explanatory variables.

    Parameters:
        df:
            A merged weekly MacroSense DataFrame.

        target_column:
            The column we want to explain. For this project, the default is stock_return.

    Returns:
        A DataFrame ranking each feature by its correlation with stock_return.
    """

    # Make a copy so we do not accidentally change the original DataFrame.
    data = df.copy()

    # These are the features we want to compare against the selected stock's return.
    feature_columns = [
        # Market and sector returns
        "market_return",
        "sector_return",

        # Macro change z-score features
        "change_10y_yield_zscore",
        "change_fed_funds_rate_zscore",
        "change_yield_curve_spread_zscore",
        "change_unemployment_rate_zscore",
        "change_credit_spread_zscore",
        "change_mortgage_rate_zscore",
        "change_vix_zscore",
        "change_oil_zscore",
        "change_cpi_zscore",
        "change_consumer_sentiment_zscore"
    ]

    # Make sure the target column exists.
    if target_column not in data.columns:
        raise ValueError(f"Missing target column: {target_column}")

    # This list will store one result row per feature.
    correlation_results = []

    # Loop through each feature and calculate its correlation with stock_return.
    for column in feature_columns:

        # Only calculate correlation if the feature exists in the dataset.
        if column in data.columns:
            correlation = data[target_column].corr(data[column])

            correlation_results.append(
                {
                    "feature": column,
                    "correlation": correlation,
                    "absolute_correlation": abs(correlation)
                }
            )

    # Convert the list of dictionaries into a DataFrame.
    correlation_df = pd.DataFrame(correlation_results)

    # Sort by absolute correlation so the strongest relationships appear first.
    correlation_df = correlation_df.sort_values(
        "absolute_correlation",
        ascending=False
    )

    # Reset index after sorting.
    correlation_df = correlation_df.reset_index(drop=True)

    return correlation_df


def run_correlation_analysis(ticker, start_date, end_date):
    """
    Run the full Day 12 correlation analysis for one ticker.

    Parameters:
        ticker:
            Stock ticker symbol, such as FICO, JPM, or XOM.
        start_date:
            Start date in "YYYY-MM-DD" format.
        end_date:
            End date in "YYYY-MM-DD" format.

    Returns:
        merged_data:
            The full merged weekly dataset.
        correlation_df:
            Ranked correlation results.
    """

    # Create the full merged dataset using the pipeline built in earlier days.
    merged_data = merge_stock_macro_data(ticker, start_date, end_date)

    # Calculate correlations against stock_return.
    correlation_df = calculate_correlations(merged_data)

    return merged_data, correlation_df

def run_return_regression(df, target_column="stock_return"):
    """
    Run a regression model to explain stock returns using
    market returns, sector returns, and macro shock variables.

    Parameters:
        df:
            A merged weekly MacroSense DataFrame.
        target_column:
            The variable we are trying to explain.
            For this project, the default is stock_return.

    Returns:
        model:
            The fitted statsmodels regression model.
        regression_data:
            The clean dataset used in the regression.
    """

    # Make a copy so we do not accidentally change the original DataFrame.
    data = df.copy()

    # These are the explanatory variables used in the first regression model.
    feature_columns = [
        "market_return",
        "sector_return",
        "change_10y_yield_zscore",
        "change_fed_funds_rate_zscore",
        "change_yield_curve_spread_zscore",
        "change_unemployment_rate_zscore",
        "change_credit_spread_zscore",
        "change_mortgage_rate_zscore",
        "change_vix_zscore",
        "change_oil_zscore",
        "change_cpi_zscore",
        "change_consumer_sentiment_zscore"
    ]

    # Make sure the target column exists.
    if target_column not in data.columns:
        raise ValueError(f"Missing target column: {target_column}")

    # Make sure every regression feature exists.
    for column in feature_columns:
        if column not in data.columns:
            raise ValueError(f"Missing regression feature column: {column}")

    # Keep only the target and feature columns.
    regression_data = data[[target_column] + feature_columns].copy()

    # Drop missing values before regression.
    regression_data = regression_data.dropna()

    # y is what we are trying to explain.
    y = regression_data[target_column]

    # X is the set of explanatory variables.
    X = regression_data[feature_columns]

    # Add a constant/intercept term to the regression.
    X = sm.add_constant(X)

    # Fit the ordinary least squares regression model.
    model = sm.OLS(y, X).fit()

    return model, regression_data

def run_full_regression_analysis(ticker, start_date, end_date):
    """
    Run the full MacroSense regression workflow for one ticker.

    Parameters:
        ticker:
            Stock ticker symbol, such as FICO, JPM, or XOM.
        start_date:
            Start date in "YYYY-MM-DD" format.
        end_date:
            End date in "YYYY-MM-DD" format.

    Returns:
        merged_data:
            The full merged weekly dataset.
        model:
            The fitted regression model.
        regression_data:
            The exact clean dataset used for the model.
    """

    # Build the full merged dataset using the existing pipeline.
    merged_data = merge_stock_macro_data(ticker, start_date, end_date)

    # Run the regression model.
    model, regression_data = run_return_regression(merged_data)

    return merged_data, model, regression_data

def create_coefficient_table(model):
    """
    Convert regression model results into a clean coefficient table.

    Parameters:
        model:
            A fitted statsmodels regression model.

    Returns:
        A DataFrame with coefficients, p-values, and absolute coefficient size.
    """

    coefficient_table = pd.DataFrame(
        {
            "feature": model.params.index,
            "coefficient": model.params.values,
            "p_value": model.pvalues.values
        }
    )

    coefficient_table["absolute_coefficient"] = coefficient_table[
        "coefficient"
    ].abs()

    coefficient_table = coefficient_table.sort_values(
        "absolute_coefficient",
        ascending=False
    )

    coefficient_table = coefficient_table.reset_index(drop=True)

    return coefficient_table

def create_attribution_table(df, model, target_column="stock_return"):
    """
    Create an attribution table showing actual return, predicted return,
    factor contributions, and residual return.

    Parameters:
        df:
            The merged weekly MacroSense DataFrame.

        model:
            A fitted statsmodels regression model.

        target_column:
            The return column being explained. Default is stock_return.

    Returns:
        A DataFrame with actual return, predicted return, contributions,
        and residual return.
    """

    # Make a copy so we do not accidentally change the original DataFrame.
    data = df.copy()

    # Make sure the target column exists.
    if target_column not in data.columns:
        raise ValueError(f"Missing target column: {target_column}")

    # Make sure all regression features exist.
    for column in REGRESSION_FEATURES:
        if column not in data.columns:
            raise ValueError(f"Missing regression feature column: {column}")

    # Keep date, target return, and regression feature columns.
    attribution_data = data[["date", target_column] + REGRESSION_FEATURES].copy()

    # Drop missing values so the rows match what the model can use.
    attribution_data = attribution_data.dropna()

    # Start the output table with date and actual stock return.
    attribution_table = attribution_data[["date", target_column]].copy()

    # Rename stock_return to actual_return for clearer interpretation.
    attribution_table = attribution_table.rename(
        columns={target_column: "actual_return"}
    )

    # Create X variables for prediction.
    X = attribution_data[REGRESSION_FEATURES]

    # Add constant because the regression model included a constant.
    X = sm.add_constant(X)

    # Calculate predicted return using the fitted regression model.
    attribution_table["predicted_return"] = model.predict(X)

    # The residual is the part of the stock return not explained by the model.
    attribution_table["residual_return"] = (
        attribution_table["actual_return"] - attribution_table["predicted_return"]
    )

    # Add the constant contribution.
    # This is the model's baseline return estimate.
    attribution_table["constant_contribution"] = model.params["const"]

    # Market contribution.
    attribution_table["market_contribution"] = (
        attribution_data["market_return"] * model.params["market_return"]
    )

    # Sector contribution.
    attribution_table["sector_contribution"] = (
        attribution_data["sector_return"] * model.params["sector_return"]
    )

    # Create separate macro contribution columns.
    macro_contribution_columns = []

    for column in REGRESSION_FEATURES:
        if column not in ["market_return", "sector_return"]:
            contribution_column = f"{column}_contribution"

            attribution_table[contribution_column] = (
                attribution_data[column] * model.params[column]
            )

            macro_contribution_columns.append(contribution_column)

    # Add all macro contribution columns into one total macro contribution.
    attribution_table["macro_contribution"] = attribution_table[
        macro_contribution_columns
    ].sum(axis=1)

    # Add a total explained contribution check.
    attribution_table["total_explained_contribution"] = (
        attribution_table["constant_contribution"]
        + attribution_table["market_contribution"]
        + attribution_table["sector_contribution"]
        + attribution_table["macro_contribution"]
    )

    # Sort by date.
    attribution_table = attribution_table.sort_values("date")

    # Reset index.
    attribution_table = attribution_table.reset_index(drop=True)

    return attribution_table

def get_largest_residual_weeks(attribution_table, n=10):
    """
    Find the weeks with the largest unexplained stock moves.

    Parameters:
        attribution_table:
            A DataFrame created by create_attribution_table().

        n:
            Number of largest residual weeks to return.

    Returns:
        A DataFrame sorted by largest absolute residual.
    """

    data = attribution_table.copy()

    if "residual_return" not in data.columns:
        raise ValueError("Missing residual_return column.")

    data["absolute_residual"] = data["residual_return"].abs()

    largest_residuals = data.sort_values(
        "absolute_residual",
        ascending=False
    ).head(n)

    largest_residuals = largest_residuals.reset_index(drop=True)

    return largest_residuals

def run_full_attribution_analysis(ticker, start_date, end_date):
    """
    Run the full MacroSense attribution workflow for one ticker.

    Returns:
        merged_data:
            Full merged weekly dataset.

        model:
            Fitted regression model.

        coefficient_table:
            Clean regression coefficient table.

        attribution_table:
            Actual vs predicted return attribution table.

        largest_residuals:
            Weeks with the largest unexplained residuals.
    """

    merged_data, model, regression_data = run_full_regression_analysis(
        ticker,
        start_date,
        end_date
    )

    coefficient_table = create_coefficient_table(model)

    attribution_table = create_attribution_table(
        merged_data,
        model,
        target_column="stock_return"
    )

    largest_residuals = get_largest_residual_weeks(
        attribution_table,
        n=10
    )

    return merged_data, model, coefficient_table, attribution_table, largest_residuals

def summarize_attribution_row(ticker, attribution_table, model, row_index=-1):
    """
    Create a plain-English summary for one row of the attribution table.

    Parameters:
        ticker:
            Stock ticker symbol, such as FICO, JPM, or XOM.

        attribution_table:
            DataFrame created by create_attribution_table().

        model:
            Fitted regression model.

        row_index:
            Which row to summarize.
            Default is -1, which means the latest row.

    Returns:
        A dictionary containing both numbers and a plain-English summary.
    """

    data = attribution_table.copy()

    if len(data) == 0:
        raise ValueError("Attribution table is empty.")

    row = data.iloc[row_index]

    date_value = row["date"]

    if hasattr(date_value, "strftime"):
        date_text = date_value.strftime("%Y-%m-%d")
    else:
        date_text = str(date_value)

    driver_values = {
        "market": row["market_contribution"],
        "sector": row["sector_contribution"],
        "macro": row["macro_contribution"],
        "residual": row["residual_return"]
    }

    main_driver = max(
        driver_values,
        key=lambda driver: abs(driver_values[driver])
    )

    main_driver_value = driver_values[main_driver]

    if row["actual_return"] > 0:
        return_direction = "rose"
    elif row["actual_return"] < 0:
        return_direction = "fell"
    else:
        return_direction = "was flat"

    if row["residual_return"] > 0:
        residual_interpretation = "outperformed what the model expected"
    elif row["residual_return"] < 0:
        residual_interpretation = "underperformed what the model expected"
    else:
        residual_interpretation = "matched what the model expected"

    macro_contribution_columns = [
        column for column in data.columns
        if column.endswith("_contribution")
        and column not in [
            "constant_contribution",
            "market_contribution",
            "sector_contribution",
            "macro_contribution",
            "total_explained_contribution"
        ]
    ]

    if len(macro_contribution_columns) > 0:
        top_macro_factor = row[macro_contribution_columns].abs().idxmax()
        top_macro_contribution = row[top_macro_factor]
    else:
        top_macro_factor = None
        top_macro_contribution = 0

    summary_text = (
        f"{ticker.upper()} {return_direction} {format_percent(row['actual_return'])} "
        f"for the week ending {date_text}. "
        f"The model predicted {format_percent(row['predicted_return'])}, "
        f"leaving a residual of {format_percent(row['residual_return'])}. "
        f"The largest overall driver was {main_driver}, contributing approximately "
        f"{format_percent(main_driver_value)}. "
        f"The model's R-squared was {model.rsquared:.2f}, meaning it explained about "
        f"{model.rsquared * 100:.1f}% of the historical weekly return variation in this sample. "
        f"Based on the residual, the stock {residual_interpretation}."
    )

    if top_macro_factor is not None:
        summary_text += (
            f" The largest individual macro contribution came from "
            f"{top_macro_factor}, at approximately "
            f"{format_percent(top_macro_contribution)}."
        )

    summary = {
        "ticker": ticker.upper(),
        "date": date_text,
        "actual_return": row["actual_return"],
        "predicted_return": row["predicted_return"],
        "market_contribution": row["market_contribution"],
        "sector_contribution": row["sector_contribution"],
        "macro_contribution": row["macro_contribution"],
        "residual_return": row["residual_return"],
        "main_driver": main_driver,
        "main_driver_contribution": main_driver_value,
        "top_macro_factor": top_macro_factor,
        "top_macro_contribution": top_macro_contribution,
        "r_squared": model.rsquared,
        "summary_text": summary_text
    }

    return summary

def create_summary_table(summary):
    """
    Convert a summary dictionary into a one-row DataFrame.

    Parameters:
        summary:
            Dictionary created by summarize_attribution_row().

    Returns:
        A one-row pandas DataFrame.
    """

    summary_table = pd.DataFrame(
        [
            {
                "ticker": summary["ticker"],
                "date": summary["date"],
                "actual_return": summary["actual_return"],
                "predicted_return": summary["predicted_return"],
                "market_contribution": summary["market_contribution"],
                "sector_contribution": summary["sector_contribution"],
                "macro_contribution": summary["macro_contribution"],
                "residual_return": summary["residual_return"],
                "main_driver": summary["main_driver"],
                "main_driver_contribution": summary["main_driver_contribution"],
                "top_macro_factor": summary["top_macro_factor"],
                "top_macro_contribution": summary["top_macro_contribution"],
                "r_squared": summary["r_squared"]
            }
        ]
    )

    return summary_table

def run_full_mvp_analysis(ticker, start_date, end_date):
    """
    Run the full MacroSense MVP workflow for one ticker.

    This includes:
        merged dataset
        regression model
        coefficient table
        attribution table
        largest residual weeks
        latest week summary
        latest week summary table
    """

    merged_data, model, coefficient_table, attribution_table, largest_residuals = run_full_attribution_analysis(
        ticker,
        start_date,
        end_date
    )

    latest_summary = summarize_attribution_row(
        ticker,
        attribution_table,
        model,
        row_index=-1
    )

    latest_summary_table = create_summary_table(latest_summary)

    return (
        merged_data,
        model,
        coefficient_table,
        attribution_table,
        largest_residuals,
        latest_summary,
        latest_summary_table
    )


def format_percent(value):
    """
    Convert a decimal return into a readable percent string.

    Example:
        0.052 becomes '5.20%'
        -0.031 becomes '-3.10%'
    """

    return f"{value * 100:.2f}%"


def summarize_attribution_row(ticker, attribution_table, model, row_index=-1):
    """
    Create a plain-English summary for one row of the attribution table.
    """

    data = attribution_table.copy()

    if len(data) == 0:
        raise ValueError("Attribution table is empty.")

    row = data.iloc[row_index]

    date_value = row["date"]

    if hasattr(date_value, "strftime"):
        date_text = date_value.strftime("%Y-%m-%d")
    else:
        date_text = str(date_value)

    driver_values = {
        "market": row["market_contribution"],
        "sector": row["sector_contribution"],
        "macro": row["macro_contribution"],
        "residual": row["residual_return"]
    }

    main_driver = max(
        driver_values,
        key=lambda driver: abs(driver_values[driver])
    )

    main_driver_value = driver_values[main_driver]

    if row["actual_return"] > 0:
        return_direction = "rose"
    elif row["actual_return"] < 0:
        return_direction = "fell"
    else:
        return_direction = "was flat"

    if row["residual_return"] > 0:
        residual_interpretation = "outperformed what the model expected"
    elif row["residual_return"] < 0:
        residual_interpretation = "underperformed what the model expected"
    else:
        residual_interpretation = "matched what the model expected"

    macro_contribution_columns = [
        column for column in data.columns
        if column.endswith("_contribution")
        and column not in [
            "constant_contribution",
            "market_contribution",
            "sector_contribution",
            "macro_contribution",
            "total_explained_contribution"
        ]
    ]

    if len(macro_contribution_columns) > 0:
        top_macro_factor = row[macro_contribution_columns].abs().idxmax()
        top_macro_contribution = row[top_macro_factor]
    else:
        top_macro_factor = None
        top_macro_contribution = 0

    summary_text = (
        f"{ticker.upper()} {return_direction} {format_percent(row['actual_return'])} "
        f"for the week ending {date_text}. "
        f"The model predicted {format_percent(row['predicted_return'])}, "
        f"leaving a residual of {format_percent(row['residual_return'])}. "
        f"The largest overall driver was {main_driver}, contributing approximately "
        f"{format_percent(main_driver_value)}. "
        f"The model's R-squared was {model.rsquared:.2f}, meaning it explained about "
        f"{model.rsquared * 100:.1f}% of the historical weekly return variation in this sample. "
        f"Based on the residual, the stock {residual_interpretation}."
    )

    if top_macro_factor is not None:
        summary_text += (
            f" The largest individual macro contribution came from "
            f"{top_macro_factor}, at approximately "
            f"{format_percent(top_macro_contribution)}."
        )

    summary = {
        "ticker": ticker.upper(),
        "date": date_text,
        "actual_return": row["actual_return"],
        "predicted_return": row["predicted_return"],
        "market_contribution": row["market_contribution"],
        "sector_contribution": row["sector_contribution"],
        "macro_contribution": row["macro_contribution"],
        "residual_return": row["residual_return"],
        "main_driver": main_driver,
        "main_driver_contribution": main_driver_value,
        "top_macro_factor": top_macro_factor,
        "top_macro_contribution": top_macro_contribution,
        "r_squared": model.rsquared,
        "summary_text": summary_text
    }

    return summary


def create_summary_table(summary):
    """
    Convert a summary dictionary into a one-row DataFrame.
    """

    summary_table = pd.DataFrame(
        [
            {
                "ticker": summary["ticker"],
                "date": summary["date"],
                "actual_return": summary["actual_return"],
                "predicted_return": summary["predicted_return"],
                "market_contribution": summary["market_contribution"],
                "sector_contribution": summary["sector_contribution"],
                "macro_contribution": summary["macro_contribution"],
                "residual_return": summary["residual_return"],
                "main_driver": summary["main_driver"],
                "main_driver_contribution": summary["main_driver_contribution"],
                "top_macro_factor": summary["top_macro_factor"],
                "top_macro_contribution": summary["top_macro_contribution"],
                "r_squared": summary["r_squared"]
            }
        ]
    )

    return summary_table


def run_full_mvp_analysis(ticker, start_date, end_date):
    """
    Run the full MacroSense MVP workflow for one ticker.
    """

    merged_data, model, coefficient_table, attribution_table, largest_residuals = run_full_attribution_analysis(
        ticker,
        start_date,
        end_date
    )

    latest_summary = summarize_attribution_row(
        ticker,
        attribution_table,
        model,
        row_index=-1
    )

    latest_summary_table = create_summary_table(latest_summary)

    return (
        merged_data,
        model,
        coefficient_table,
        attribution_table,
        largest_residuals,
        latest_summary,
        latest_summary_table
    )