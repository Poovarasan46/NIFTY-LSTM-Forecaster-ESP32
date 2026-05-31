import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping

# =====================================================
# LOAD DATA
# =====================================================

print("Loading data...")

df = pd.read_csv("data/nifty.csv", skiprows=2)

# Rename columns
df.columns = [
    "Date",
    "Close",
    "High",
    "Low",
    "Open",
    "Volume"
]

# Convert to numeric
numeric_cols = [
    "Close",
    "High",
    "Low",
    "Open",
    "Volume"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove missing values
df = df.dropna()

print("\nDataset Shape:")
print(df.shape)

print("\nData Types:")
print(df.dtypes)

# =====================================================
# FEATURES
# =====================================================

features = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]

data = df[features].values

# =====================================================
# SCALE DATA
# =====================================================

print("\nScaling data...")

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# =====================================================
# CREATE SEQUENCES
# =====================================================

print("Creating sequences...")

sequence_length = 60

X = []
y = []

for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i])

    # Predict Close price
    y.append(scaled_data[i, 3])

X = np.array(X)
y = np.array(y)

print("\nShapes:")
print("X shape:", X.shape)
print("y shape:", y.shape)

# =====================================================
# TRAIN TEST SPLIT
# =====================================================

split_index = int(len(X) * 0.8)

X_train = X[:split_index]
y_train = y[:split_index]

X_test = X[split_index:]
y_test = y[split_index:]

print("\nTraining Samples:", len(X_train))
print("Testing Samples :", len(X_test))

# =====================================================
# BUILD MODEL
# =====================================================

print("\nBuilding LSTM model...")

model = Sequential([
    Input(shape=(60, 5)),

    LSTM(
        units=64,
        return_sequences=True
    ),

    Dropout(0.2),

    LSTM(
        units=64
    ),

    Dropout(0.2),

    Dense(25),

    Dense(1)
])

model.compile(
    optimizer="adam",
    loss="mean_squared_error"
)

model.summary()

# =====================================================
# TRAIN MODEL
# =====================================================

print("\nStarting training...")

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

history = model.fit(
    X_train,
    y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
    callbacks=[early_stop],
    verbose=1
)

# =====================================================
# SAVE MODEL
# =====================================================

import os

os.makedirs("model", exist_ok=True)

model.save("model/nifty_lstm.keras")

print("\nModel saved successfully!")
print("Location: model/nifty_lstm.keras")

# =====================================================
# EVALUATE MODEL
# =====================================================

print("\nEvaluating model...")

predictions = model.predict(X_test)

dummy_pred = np.zeros((len(predictions), 5))
dummy_actual = np.zeros((len(y_test), 5))

dummy_pred[:, 3] = predictions[:, 0]
dummy_actual[:, 3] = y_test

predicted_close = scaler.inverse_transform(dummy_pred)[:, 3]
actual_close = scaler.inverse_transform(dummy_actual)[:, 3]

mae = mean_absolute_error(
    actual_close,
    predicted_close
)

print("\n================================")
print("Mean Absolute Error (MAE):")
print(mae)
print("================================")

# =====================================================
# NEXT DAY PREDICTION
# =====================================================

last_60_days = scaled_data[-60:]

X_future = np.array([last_60_days])

future_prediction = model.predict(X_future)

dummy_future = np.zeros((1, 5))
dummy_future[:, 3] = future_prediction[:, 0]

next_close = scaler.inverse_transform(dummy_future)[0, 3]

print("\nPredicted Next NIFTY Close:")
print(round(next_close, 2))

print("\nTraining Complete!")