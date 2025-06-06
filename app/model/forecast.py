
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import logging
import numpy as np
import polars as pl
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Input
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, BatchNormalization, Dropout
from tensorflow.keras.losses import MeanSquaredError


MODELS_DIR = "saved_models"
os.makedirs(MODELS_DIR, exist_ok=True)

def prepare_data(df: pl.DataFrame, window_size: int = 60):
    logging.info(f"data features: {df.columns}")
    values = df.select("price").to_numpy()

    if values.shape[0] < window_size:
        raise ValueError(
           f"insufficient data for window size {window_size}, found {values.shape[0]} rows"
        )

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    logging.info(f"Scaled data: {scaled.shape}")
    logging.info(f"Original data: {values}")

    X, y = [], []
    for i in range(window_size, len(scaled)):
        # logging.info(f"Processing index {i} for window size {window_size}")
        X.append(scaled[i-window_size:i])
        y.append(scaled[i])
    
    logging.info(f"Prepared {len(X)} samples with window size {window_size}")
    logging.info(f"Prepared {len(y)} samples with window size {window_size}")

    return np.array(X), np.array(y), scaler

def build_model(input_shape):
    logging.info(f"Building model with input shape: {input_shape}")
    model = Sequential([
        Input(shape=input_shape),
        LSTM(100, return_sequences=True),
        BatchNormalization(),
        Dropout(0.2),
        LSTM(100, return_sequences=True), 
        BatchNormalization(), 
        Dropout(0.2), 
        LSTM(50),
        Dense(20, activation='relu'),
        Dense(1)
    ])
    logging.info("Compiling model with Adam optimizer and Mean Squared Error loss")
    model.compile(optimizer='adam', loss=MeanSquaredError())
    return model

def get_model_filename(ticker: str, window_size: int):
    logging.info(f"Generating model filename for ticker: {ticker}, window size: {window_size}")
    return os.path.join(MODELS_DIR, f"{ticker.lower()}_ws{window_size}.keras")

def save_model(model, filename):
    logging.info(f"Saving model to {filename}")
    model.save(filename)

def load_existing_model(filename):
    logging.info(f"Loading existing model from {filename}")
    return load_model(filename, compile=True, custom_objects={"MeanSquaredError": MeanSquaredError})
