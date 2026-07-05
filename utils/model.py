import streamlit as st
import joblib
import pandas as pd
import os
from utils.preprocessing import status_downtime

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "xgboost_chain_model_24h.joblib")

@st.cache_resource
def load_model():
    """Memuat model RegressorChain dari file joblib."""
    return joblib.load(MODEL_PATH)

def future_pred_clean_df(last_time, future_pred_df, horizon):
    future_clean = {
        'temperature_C_pred': [],
        'vibration_mm_s_pred': [],
        'pressure_bar_pred': []
    }

    for i in range(future_pred_df.shape[0]):
        if i % 3 == 0:
            future_clean['temperature_C_pred'].append(float(future_pred_df.iloc[i].values[0]))
        elif i % 3 == 1:
            future_clean['vibration_mm_s_pred'].append(float(future_pred_df.iloc[i].values[0]))
        else:
            future_clean['pressure_bar_pred'].append(float(future_pred_df.iloc[i].values[0]))

    time_future = pd.date_range(start=last_time + pd.Timedelta(hours=1), periods=horizon, freq='1H')
    future_clean_df = pd.DataFrame(future_clean, index=time_future)
    future_clean_df['status'] = future_clean_df.apply(status_downtime, axis=1)

    temp_pred = future_clean_df['temperature_C_pred'].values
    vib_pred = future_clean_df['vibration_mm_s_pred'].values
    pres_pred = future_clean_df['pressure_bar_pred'].values
    status = future_clean_df['status'].values
    return time_future, temp_pred, vib_pred, pres_pred, status

def run_prediction(model, last_time, X_input, TARGETS, horizon):
    """Run batch prediction and parse results.
    Args:
        model: loaded sklearn model
        X_input: numpy array of shape (n_rows, 6)
        HORIZON: number of time steps to predict
    Returns:
        list of dicts with keys: idx, temp_pred, vib_pred, pres_pred,
        avg_temp, avg_vib, avg_pres, max_temp, max_vib, max_pres, input
        Or raises an exception.
    """
    y_pred = model.predict(X_input).flatten()
    y_pred_df = pd.DataFrame(y_pred, index=TARGETS)
    time_future, temp_pred, vib_pred, pres_pred, status = future_pred_clean_df(last_time, y_pred_df, horizon)
    
    results = []
    results.append({
        "time_future": time_future,
        "temp_pred": temp_pred,
        "vib_pred": vib_pred,
        "pres_pred": pres_pred,
        "avg_temp": float(temp_pred.mean()),
        "avg_vib": float(vib_pred.mean()),
        "avg_pres": float(pres_pred.mean()),
        "max_temp": float(temp_pred.max()),
        "max_vib": float(vib_pred.max()),
        "max_pres": float(pres_pred.max()),
        "status": status
    })
    return results
