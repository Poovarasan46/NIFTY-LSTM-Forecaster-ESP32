import os
import numpy as np
import pandas as pd

from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# ==================================================
# ABSOLUTE PATHS
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "nifty_lstm.keras"
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "nifty.csv"
)

# ==================================================
# MAIN FUNCTION
# ==================================================

def get_prediction():

    model = load_model(MODEL_PATH)

    df = pd.read_csv(
        DATA_PATH,
        skiprows=2
    )

    df.columns = [
        "Date",
        "Close",
        "High",
        "Low",
        "Open",
        "Volume"
    ]

    for col in [
        "Close",
        "High",
        "Low",
        "Open",
        "Volume"
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna()

    features = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    data = df[features].values

    scaler = MinMaxScaler()

    scaled_data = scaler.fit_transform(
        data
    )

    # Last 60 candles

    X = np.array([
        scaled_data[-60:]
    ])

    prediction = model.predict(
        X,
        verbose=0
    )

    dummy = np.zeros((1,5))

    dummy[:,3] = prediction[:,0]

    predicted_close = (
        scaler.inverse_transform(dummy)
    )[0,3]

    current_close = (
        df["Close"].iloc[-1]
    )

    trend = (
        "UP"
        if predicted_close > current_close
        else "DOWN"
    )

    change = abs(
        predicted_close -
        current_close
    )

    confidence = max(
        50,
        min(
            95,
            int(
                95 -
                (
                    change /
                    current_close
                ) * 1000
            )
        )
    )

    chart_data = (
        df["Close"]
        .tail(30)
        .tolist()
    )

    return {
        "current":
            round(
                float(current_close),
                2
            ),

        "predicted":
            round(
                float(predicted_close),
                2
            ),

        "trend":
            trend,

        "confidence":
            confidence,

        "chart":
            chart_data
    }


if __name__ == "__main__":

    result = get_prediction()

    print(result)