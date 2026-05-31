import pandas as pd

def add_indicators(df):

    # 20 Day Moving Average
    df["MA20"] = (
        df["Close"]
        .rolling(20)
        .mean()
    )

    # 50 Day Moving Average
    df["MA50"] = (
        df["Close"]
        .rolling(50)
        .mean()
    )

    return df