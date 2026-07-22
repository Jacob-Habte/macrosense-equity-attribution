import pandas as pd # Pandas handles tables
import yfinance as yf # yf pulls market data

SECTOR_TO_ETF = {
    "technology": "XLK",
    "financial services": "XLF",
    "financials": "XLF",
    "energy": "XLE",
    "consumer cyclical": "XLY",
    "consumer discretionary": "XLY",
    "industrials": "XLI",
    "healthcare": "XLV",
    "health care": "XLV",
    "consumer defensive": "XLP",
    "consumer staples": "XLP",
    "utilities": "XLU",
    "real estate": "XLRE",
    "communication services": "XLC",
    "basic materials": "XLB",
    "materials": "XLB"
}

FALLBACK_TICKER_TO_ETF = {
    "FICO": "XLK",
    "AAPL": "XLK",
    "MSFT": "XLK",
    "JPM": "XLF",
    "XOM": "XLE"
}

BENCHMARK_TICKERS = [
    "SPY",
    "QQQ",
    "XLK",
    "XLF",
    "XLE",
    "XLY",
    "XLI",
    "XLV",
    "XLP",
    "XLU",
    "XLRE",
    "XLC",
    "XLB"
]


def clean_sector_name(sector_name):
    """
    Standardize sector text so it can be matched to SECTOR_TO_ETF.
    """

    if sector_name is None:
        return None

    return str(sector_name).strip().lower()


def get_ticker_profile(ticker):
    """
    Pull basic company metadata from yfinance.

    Returns:
        A dictionary with ticker, company name, sector, industry, quote type, and currency.
    """

    ticker = ticker.upper()

    yf_ticker = yf.Ticker(ticker)

    try:
        info = yf_ticker.info
    except Exception:
        info = {}

    # Try multiple possible name fields.
    # yfinance does not always return longName for every ticker.
    company_name = (
        info.get("longName")
        or info.get("shortName")
        or info.get("displayName")
        or info.get("name")
        or ticker
    )

    profile = {
        "ticker": ticker,
        "long_name": company_name,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "quote_type": info.get("quoteType"),
        "currency": info.get("currency")
    }

    return profile

def get_sector_etf(ticker, fallback_to_market=True):
    """
    Return the best sector ETF for a ticker.

    First, use manual fallbacks for known MVP tickers.
    Then, try to pull the sector from yfinance.
    If no sector match is found, optionally fall back to SPY.
    """

    ticker = ticker.upper()

    if ticker in FALLBACK_TICKER_TO_ETF:
        return FALLBACK_TICKER_TO_ETF[ticker]

    profile = get_ticker_profile(ticker)

    sector = clean_sector_name(profile.get("sector"))

    if sector in SECTOR_TO_ETF:
        return SECTOR_TO_ETF[sector]

    if fallback_to_market:
        return "SPY"

    raise ValueError(
        f"No sector ETF mapping found for ticker: {ticker}. "
        f"Detected sector: {profile.get('sector')}"
    )

"""
1. Pull stock price data from yfinance
2. Check if the ticker actually returned data
3. Move the date from the index into a normal column
4. Keep only the useful columns
5. Rename the columns cleanly and return the table
"""

def get_stock_prices(ticker, start_date, end_date):
    """
    Pull historical stock price data for a given ticker.

    Prm's:
        ticker: stock ticker
        start_date: start date, 'YYYY-MM-DD' form
        end_date: end date, 'YYYY-MM-DD' form
    
    Return: Pandas DataFrame w/ date, open, high, low, close, adj close, and volume
    """
    # auto_adjust = false, ensures both close and adj close are both in the returned data; progress = false hides the download progress bar
    data = yf.download(ticker, start = start_date, end = end_date, auto_adjust=False, progress=False)

    if data.empty:
        raise ValueError(f"No data found for ticker: {ticker}")
    
    # Flattens columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    # We want date to be a regulur column not a index as later want to merge stock data w/ market, sector, and macro data by date
    data = data.reset_index()

    first_column = data.columns[0]
    data = data.rename(columns={first_column: "date"})

    # Rename the yfinance columns to cleaner Python-style column names.
    data = data.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Adj Close": "adjusted_close", "Volume": "volume"})

    # These are the columns we expect the final table to have.
    required_columns = ["date", "open", "high", "low", "close", "adjusted_close", "volume"]

    # Check if any required columns are missing.
    missing_columns = []

    # Loop through each column name and check if the required column is NOT in the DataFrame, add the missing column name to the missing_columns list 
    for column in required_columns:
        if column not in data.columns:
            missing_columns.append(column)

    # See if any columns were missing after checking all required columns, stop function and give error message
    if len(missing_columns) > 0:
        raise ValueError(
            f"Missing columns: {missing_columns}. "
            f"Available columns: {list(data.columns)}"
        )

    # Return only the clean/required columns in the order we want.
    data = data[required_columns]

    data.columns.name = None

    return data


def calculate_returns(price_df, frequency="weekly"):
    """
    Convert stock price data into returns.
    
    Prm's:
        price_df:
            Pandas DataFrame from get_stock_prices()
        frequency:
            Return frequency wanted.
            Options: "daily", "weekly", "monthly"
                 
    Return:
        Pandas DataFrame with date, adjusted_close, return
    """

    # Make a copy of the table.
    data = price_df.copy()

    # Make sure date is treated as a datetime column.
    data["date"] = pd.to_datetime(data["date"])

    # Sort data from oldest to newest.
    data = data.sort_values("date")

    # Keep only the columns needed for return calculation.
    data = data[["date", "adjusted_close"]]

    # Set date as the index so we can resample by time.
    data = data.set_index("date")

    # Based on the chosen frequency, convert adjusted close prices into returns.
    if frequency == "daily":
        returns = data.copy()
        returns["return"] = returns["adjusted_close"].pct_change()

    elif frequency == "weekly":
        weekly_prices = data.resample("W-FRI").last()
        returns = weekly_prices.copy()
        returns["return"] = returns["adjusted_close"].pct_change()

    elif frequency == "monthly":
        monthly_prices = data.resample("ME").last()
        returns = monthly_prices.copy()
        returns["return"] = returns["adjusted_close"].pct_change()

    else:
        raise ValueError("frequency must be 'daily', 'weekly', or 'monthly'")
    
    # The first return is missing because there is no previous period to compare to.
    returns = returns.dropna()

    # Move date from index back into a normal column.
    returns = returns.reset_index()

    # Keep only the clean final columns.
    returns = returns[["date", "adjusted_close", "return"]]

    returns.columns.name = None

    return returns

"""
1. Starts with an empty benchmark table
2. Loops through each ETF ticker
3. Pulls that ETF’s prices
4. Converts those prices into returns
5. Merges each ETF return column into one table by date
"""

def get_benchmark_returns(start_date, end_date, frequency="weekly"):
    """
    Pull benchmark ETF prices and convert them into returns.

    Prm's:
        start_date: start date, 'YYYY-MM-DD' form
        end_date: end date, 'YYYY-MM-DD' form
        frequency: Return frequency, default is weekly as MacroSense should use weekly returns mainly
    Returns:
        A pandas DataFrame where each row is a date and each column is an ETF return
    """

    benchmark_returns = None

    # For a ticker in our benchmark tickers, grab its prices and returns via previous functions, merge a etf returns with the returns table and rename the column to be {the ticker}_returns
    for ticker in BENCHMARK_TICKERS:
        prices = get_stock_prices(ticker, start_date, end_date)
        returns = calculate_returns(prices, frequency=frequency)

        returns = returns[["date", "return"]].rename(columns={"return": f"{ticker.lower()}_return"})

        if benchmark_returns is None:
            benchmark_returns = returns
        
        else:
            benchmark_returns = benchmark_returns.merge(returns, on="date", how="inner")

    return benchmark_returns