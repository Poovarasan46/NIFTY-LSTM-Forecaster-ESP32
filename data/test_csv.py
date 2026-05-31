import pandas as pd


df = pd.read_csv("data/nifty.csv", skiprows=2)

df.columns = [
    "Date",
    "Close",
    "High",
    "Low",
    "Open",
    "Volume"
]

print(df["Close"].iloc[-1])