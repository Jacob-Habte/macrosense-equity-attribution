import pandas as pd # Pandas handles tables
import yfinance as yf # yf pulls market data

# Sector EFT Map
# Tells the model which sector ETF should be used as the compaison benchmark for each stock
SECTOR_ETF_MAP = {
    "AAPL": "XLK",
    "MSFT": "XLK",
    "FICO": "XLK",
    "JPM": "XLF",
    "XOM": "XLE"
}

# Benchmark ETF's used in MVP, SPY and QQQ for broad market movement, XL for sector level movement
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
    "XLRE"
]

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
            Return frequence wanted
            Options:
                "daily", "weekly, "monthly"
                 
    Return:
        Pandas DrataFrame with date, adjusted_close, return
          
    """

    # Make a copy of table, make sure data column treated as datetime column, sort data from oldest to newest, extract columns needed for return calculation, and set the date as the index
    data = price_df.copy()
    data["data"] = pd.to_datetime(data["date"])
    data.sort_values("date")
    date = data[["date", "adjusted_close"]]
    data = data.set_index("date")

    # Based on the chosen frequency, convert adjusted close prices into daily, weekly, or monthly returns by comparing each period's ending price to the previous period's ending price.
    # Provide options for less frequent as daily data can be to loud
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
        raise ValueError("frequency must be 'daily', 'weekly', 'monthly'")
    
    #First return will be absent of data due to having nothing to compare to, dropna removes N/A returns
    returns = returns.dropna()

    #Move date backf the index into a normal column
    returns = returns.reset_index()

    #Keep only the clean final columns
    returns = returns[["date", "adjusted_close", "return"]]

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

def get_sector_etf(ticker):
    """
    Return the sector ETF for a given stock ticker.

    Example:
        get_sector_etf("JPM") returns "XLF"
    """

    ticker = ticker.upper()

    if ticker not in SECTOR_ETF_MAP:
        raise ValueError(f"No sector ETF mapping found for ticker: {ticker}")

    return SECTOR_ETF_MAP[ticker]