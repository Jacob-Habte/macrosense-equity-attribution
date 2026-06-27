import pandas as pd # Pandas handles tables
import yfinance as yf # yf pulls market data

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
    # This helps us get a clear error instead of a confusing pandas KeyError.
    missing_columns = []

    # Loop through each column name and check if the required column is NOT in the DataFrame, add the missing column name to the missing_columns list 
    for column in required_columns:
        if column not in data.columns:
            missing_columns.append(column)

    # See if any columns were missing after checking all required columns, stop function and give errpr message
    if len(missing_columns) > 0:
        raise ValueError(
            f"Missing columns: {missing_columns}. "
            f"Available columns: {list(data.columns)}"
        )

    # Return only the clean/required columns in the order we want.
    data = data[required_columns]

    return data



