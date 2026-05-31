import yfinance as yf

data = yf.download("^NSEI", start="2018-01-01")

data.to_csv("nifty.csv")