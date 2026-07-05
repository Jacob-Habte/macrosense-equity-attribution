import os

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

# Left side is clean column names, right side is the FRED series code. Pull FRED sries code on right side, name is the name on the left side
MACRO_SERIES = {
    "ten_year_yield": "DGS10",
    "fed_funds_rate": "FEDFUNDS",
    "yield_curve_spread": "T10Y2Y",
    "cpi": "CPIAUCSL",
    "unemployment_rate": "UNRATE",
    "consumer_sentiment": "UMCSENT",
    "vix": "VIXCLS",
    "credit_spread": "BAA10Y",
    "oil_price": "DCOILWTICO",
    "mortgage_rate": "MORTGAGE30US"
}

def get_fred_client():
    """
    Create and return a FRED API client.

    API key stored in .env not code in order to keep it private
    """

    # Load env. variables from the .env file
    load_dotenv()

    api_key = os.getenv("FRED_API_KEY")

    if api_key is None:
        raise ValueError("FRED_API_KEY not found. Add to .env file")
    
    #Create FRED client using api key
    fred = Fred(api_key=api_key)

    return fred

def get_macro_series(start_date, end_date):
    """
    Pull all macro indicators from FRED.

    Prm's:
        start_date:
            Start date in "YYYY-MM-DD" format.
        end_date:
            End date in "YYYY-MM-DD" format.

    Returns:
        pandas DataFrame with date and macro indicator columns.
    """

    fred = get_fred_client()

    macro_data = None

    for macro_name, series_id in MACRO_SERIES.items():
        series = fred.get_series(
            series_id,
            observation_start=start_date,
            observation_end=end_date
        )

        series_df = series.reset_index()
        series_df.columns = ["date", macro_name]

        if macro_data is None:
            macro_data = series_df
        else:
            macro_data = macro_data.merge(
                series_df,
                on="date",
                how="outer"
            )

    macro_data = macro_data.sort_values("date")
    macro_data = macro_data.reset_index(drop=True)

    return macro_data


def get_macro_data(start_date, end_date):
    """
    Backward-compatible function name from Day 7.
    It now pulls the full Day 8 macro basket.
    """

    return get_macro_series(start_date, end_date)