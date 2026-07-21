import pandas as pd

from market_data import (
    get_stock_prices,
    calculate_returns,
    get_benchmark_returns,
    get_sector_etf
)

from macro_data import get_macro_series

def convert_macro_to_weekly(macro_df):
    """
    Convert raw macroeconomic data into weekly frequency

    Prm's:
        macro_df: A DataFrame from get_macro_series()
    Returns:
        Weekly macro DataFrame where each row represents one week.
    """

    data = macro_df.copy()

    data["date"] = pd.to_datetime(data["date"])

    data = data.sort_values("date")

    data = data.set_index("date")

    weekly_macro = data.resample("W-FRI").last()

    weekly_macro = weekly_macro.ffill()

    weekly_macro = weekly_macro.reset_index()

    return weekly_macro

def create_z_score_features(df):
    """
    Create z-score features for macro change columns.
    """

    data = df.copy()

    macro_change_columns = [
        "change_10y_yield",
        "change_fed_funds_rate",
        "change_yield_curve_spread",
        "change_unemployment_rate",
        "change_credit_spread",
        "change_mortgage_rate",
        "change_vix",
        "change_oil",
        "change_cpi",
        "change_consumer_sentiment"
    ]

    for column in macro_change_columns:
        if column not in data.columns:
            raise ValueError(f"Missing macro change column: {column}")

        column_mean = data[column].mean()
        column_std = data[column].std()

        if column_std == 0:
            data[f"{column}_zscore"] = 0
        else:
            data[f"{column}_zscore"] = (data[column] - column_mean) / column_std

    return data

def merge_stock_macro_data(ticker, start_date, end_date):
    """
    Merge stock returns, benchmark returns, sector returns, and macro data onto one weekly timeline

    Prm's:
        ticker: Stock ticker symbol
        start_date: Start date in "YYYY-MM-DD" format
        end_date: End date in "YYYY-MM-DD" format.

    Returns:
        A merged weekly DataFrame for the chosen ticker.
    """

    ticker = ticker.upper()

    stock_prices = get_stock_prices(ticker, start_date, end_date)
    stock_returns = calculate_returns(stock_prices, frequency="weekly")

    stock_returns = stock_returns.rename(columns={"adjusted_close":"stock_adjusted_close", "return":"stock_return"})

    benchmark_returns = get_benchmark_returns(start_date, end_date, frequency="weekly")
    
    sector_etf = get_sector_etf(ticker)

    sector_return_column = f"{sector_etf.lower()}_return"

    if sector_return_column not in benchmark_returns.columns:
        raise ValueError(f"Missing sector return column: {sector_return_column}")
    
    macro_data = get_macro_series(start_date, end_date)

    weekly_macro = convert_macro_to_weekly(macro_data)

    merged_data = stock_returns.merge(benchmark_returns, on="date", how="inner")

    merged_data["market_return"] = merged_data["spy_return"]

    merged_data["sector_return"] = merged_data[sector_return_column]

    merged_data = merged_data.merge(
        weekly_macro,
        on="date",
        how="left"
    )

    merged_data = merged_data.sort_values("date")

    merged_data = merged_data.ffill()

    merged_data = merged_data.dropna(
        subset=["stock_return", "market_return", "sector_return"]
    )

    merged_data = merged_data.reset_index(drop=True)

    # Create macro change features after the full weekly dataset has been merged.
    merged_data = create_macro_features(merged_data)

    # Create z-score features so macro moves can be compared on the same scale.
    merged_data = create_z_score_features(merged_data)

    merged_data.columns.name = None

    return merged_data

def create_macro_features(df):
    """
    Create macro change features from raw macro levels.

    Parameters:
        df:
            A merged weekly DataFrame containing stock returns,
            benchmark returns, sector returns, and macro variables.

    Returns:
        A DataFrame with additional macro change columns.
    """

    # Make a copy so we do not accidentally change the original DataFrame.
    data = df.copy()

    # Sort by date to make sure changes are calculated in the correct order.
    data = data.sort_values("date")

    # Rate-like variables:
    # These are already measured as percentages or spreads,
    # so we use simple differences instead of percent changes.
    data["change_10y_yield"] = data["ten_year_yield"].diff()
    data["change_fed_funds_rate"] = data["fed_funds_rate"].diff()
    data["change_yield_curve_spread"] = data["yield_curve_spread"].diff()
    data["change_unemployment_rate"] = data["unemployment_rate"].diff()
    data["change_credit_spread"] = data["credit_spread"].diff()
    data["change_mortgage_rate"] = data["mortgage_rate"].diff()

    # Price-like or index-like variables:
    # These are better measured using percent change.
    data["change_vix"] = data["vix"].pct_change()
    data["change_oil"] = data["oil_price"].pct_change()
    data["change_cpi"] = data["cpi"].pct_change()
    data["change_consumer_sentiment"] = data["consumer_sentiment"].pct_change()

    # The first row will have missing change values because there is no previous week
    # to compare against, so we remove it.
    data = data.dropna()

    # Reset index after dropping missing rows.
    data = data.reset_index(drop=True)

    return data