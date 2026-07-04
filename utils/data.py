import pandas as pd

FEATURES = [
    "temperature_C_lag_1", "temperature_C_lag_24",
    "vibration_mm_s_lag_1", "vibration_mm_s_lag_24",
    "pressure_bar_lag_1", "pressure_bar_lag_24",
    "day_of_week", "is_holiday"
]

HORIZON = 24
COLUMNS_TARGETS = ["temperature_C_t", "vibration_mm_s_t", "pressure_bar_t"]
# Format temperature_C_t_1, vibration_mm_s_t_1, pressure_bar_t_1, temperature_C_t_2, vibration_mm_s_t_2, pressure_bar_t_2, ..., temperature_C_t_24, vibration_mm_s_t_24, pressure_bar_t_24
TARGETS = [f"{feature}_{i}" for i in range(1, HORIZON + 1) for feature in COLUMNS_TARGETS]


def auto_detect_columns(df):
    """Auto-detect and rename CSV columns to standard format.
    Returns renamed DataFrame or None if columns not found.
    """
    cols_lower = {c.lower().strip().replace(" ", "_"): c for c in df.columns}
    patterns = {
        "temperature_lag1": ["temperature_lag1", "temp_lag1", "suhu_lag1", "temperature_lag_1", "temp_lag_1"],
        "temperature_lag24": ["temperature_lag24", "temp_lag24", "suhu_lag24", "temperature_lag_24", "temp_lag_24"],
        "vibration_lag1": ["vibration_lag1", "vib_lag1", "getaran_lag1", "vibration_lag_1", "vib_lag_1"],
        "vibration_lag24": ["vibration_lag24", "vib_lag24", "getaran_lag24", "vibration_lag_24", "vib_lag_24"],
        "pressure_bar_lag1": ["pressure_bar_lag1", "pressure_lag1", "pres_lag1", "tekanan_lag1", "pressure_bar_lag_1", "pressure_lag_1"],
        "pressure_bar_lag24": ["pressure_bar_lag24", "pressure_lag24", "pres_lag24", "tekanan_lag24", "pressure_bar_lag_24", "pressure_lag_24"],
    }
    rename_map = {}
    for target, candidates in patterns.items():
        found = False
        for cand in candidates:
            if cand in cols_lower:
                rename_map[cols_lower[cand]] = target
                found = True
                break
        if not found:
            return None
    return df.rename(columns=rename_map)

def validate_csv(df):
    """Validate CSV data, remove NaN rows.
    Returns (df_clean, warning_message_or_None).
    """
    # df_features = df[EXPECTED_COLUMNS]
    warning = None
    if df.isnull().any().any():
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        warning = f"Terdapat {null_cols.sum()} nilai kosong (NaN) di kolom: {', '.join(null_cols.index.tolist())}. Baris dengan NaN akan dilewati."
        valid_mask = ~df.isnull().any(axis=1)
        df = df[valid_mask].reset_index(drop=True)
    return df, warning

def get_risk_status(value, thresholds):
    """Return (status_key, label) based on threshold.
    thresholds: {'warning': float, 'danger': float}
    """
    if value >= thresholds["danger"]:
        return "danger", "🔴 BAHAYA"
    elif value >= thresholds["warning"]:
        return "warning", "🟡 WASPADA"
    else:
        return "safe", "🟢 AMAN"

def compute_risk_for_results(all_results, thresholds):
    """Add risk_status key to each result dict.
    thresholds: {'temp': {'warning':..,'danger':..}, 'vib': {...}, 'pres': {...}}
    """
    risk_levels = {"safe": 0, "warning": 1, "danger": 2}
    overall_map = {0: "safe", 1: "warning", 2: "danger"}
    for r in all_results:
        ts, _ = get_risk_status(r["max_temp"], thresholds["temp"])
        vs, _ = get_risk_status(r["max_vib"], thresholds["vib"])
        ps, _ = get_risk_status(r["max_pres"], thresholds["pres"])
        overall = max(risk_levels[ts], risk_levels[vs], risk_levels[ps])
        r["risk_status"] = overall_map[overall]
    return all_results

def create_export_dataframe(all_results):
    """Create a flat DataFrame for export with all predictions."""
    rows = []
    for r in all_results:
        for s in range(24):
            rows.append({
                # "data_ke": r["idx"] + 1,
                "step": s + 1,
                "temperature": r["temp_pred"][s],
                "vibration": r["vib_pred"][s],
                "pressure_bar": r["pres_pred"][s],
            })
    return pd.DataFrame(rows)

def create_summary_dataframe(all_results):
    """Create summary DataFrame for display."""
    risk_emoji = {"safe": "🟢 Aman", "warning": "🟡 Waspada", "danger": "🔴 Bahaya"}
    rows = []
    for r in all_results:
        rows.append({
            "Avg Temp (°C)": round(r["avg_temp"], 4),
            "Max Temp (°C)": round(r["max_temp"], 4),
            "Avg Vib (mm/s)": round(r["avg_vib"], 6),
            "Max Vib (mm/s)": round(r["max_vib"], 6),
            "Avg Pres (bar)": round(r["avg_pres"], 4),
            "Max Pres (bar)": round(r["max_pres"], 4),
            "Status Risiko": risk_emoji.get(r["risk_status"], "?"),
        })
    import pandas as pd
    return pd.DataFrame(rows).reset_index().rename(columns={"index": "Data ke-"}).set_index("Data ke-")
