import yfinance as yf

print("Downloading latest NIFTY data...")

data = yf.download(
    "^NSEI",
    period="5y"
)

data.to_csv("../data/nifty.csv")

print("Data Updated Successfully")