import streamlit as st
import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "xgboost_chain_model_24h.joblib")

@st.cache_resource
def load_model():
    """Memuat model RegressorChain dari file joblib."""
    return joblib.load(MODEL_PATH)

def parse_prediction(y_pred_row):
    """Parse output prediksi satu baris menjadi 3 array (temp, vib, pres).
    Returns (temp_pred, vib_pred, pres_pred) or (None, None, None) on failure.
    """
    y_flat = y_pred_row.flatten()
    n_steps = 24
    n_features = 3
    if len(y_flat) == n_steps * n_features:
        return y_flat[0:24], y_flat[24:48], y_flat[48:72]
    else:
        try:
            reshaped = y_flat.reshape(n_steps, n_features)
            return reshaped[:, 0], reshaped[:, 1], reshaped[:, 2]
        except Exception:
            return None, None, None

def run_prediction(model, X_input):
    """Run batch prediction and parse results.
    Args:
        model: loaded sklearn model
        X_input: numpy array of shape (n_rows, 6)
    Returns:
        list of dicts with keys: idx, temp_pred, vib_pred, pres_pred,
        avg_temp, avg_vib, avg_pres, max_temp, max_vib, max_pres, input
        Or raises an exception.
    """
    y_pred_all = model.predict(X_input)
    print(f"y_pred_all: {y_pred_all}")
    print(f"y_pred_all shape: {y_pred_all.shape}")
    n_rows = X_input.shape[0]

    results = []
    for i in range(n_rows):
        if y_pred_all.ndim == 1:
            pred_row = y_pred_all
        else:
            pred_row = y_pred_all[i]
        temp_pred, vib_pred, pres_pred = parse_prediction(pred_row)
        if temp_pred is None:
            raise ValueError(f"Format output model tidak sesuai pada baris {i + 1}. Diterima {len(pred_row.flatten())} kolom, ekspektasi 72.")
        results.append({
            "idx": i,
            "temp_pred": temp_pred,
            "vib_pred": vib_pred,
            "pres_pred": pres_pred,
            "avg_temp": float(temp_pred.mean()),
            "avg_vib": float(vib_pred.mean()),
            "avg_pres": float(pres_pred.mean()),
            "max_temp": float(temp_pred.max()),
            "max_vib": float(vib_pred.max()),
            "max_pres": float(pres_pred.max()),
        })
    return results
