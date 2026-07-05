import pandas as pd

HORIZON = 24
COLUMNS_TARGETS = ["temperature_C_t", "vibration_mm_s_t", "pressure_bar_t"]
FEATURES = [
    "temperature_C_lag_1", "temperature_C_lag_24",
    "vibration_mm_s_lag_1", "vibration_mm_s_lag_24",
    "pressure_bar_lag_1", "pressure_bar_lag_24",
    "day_of_week", "is_holiday"
]
# Format temperature_C_t_1, vibration_mm_s_t_1, pressure_bar_t_1, temperature_C_t_2, vibration_mm_s_t_2, pressure_bar_t_2, ..., temperature_C_t_24, vibration_mm_s_t_24, pressure_bar_t_24
TARGETS = [f"{feature}_{i}" for i in range(1, HORIZON + 1) for feature in COLUMNS_TARGETS]


def create_export_dataframe(all_results):
    """Create a flat DataFrame for export with all predictions."""
    rows = []
    for r in all_results:
        for s in range(24):
            rows.append({
                "Datetime": r["time_future"][s],
                "step": s + 1,
                "Temperature (°C)": r["temp_pred"][s],
                "Vibration (mm/s)": r["vib_pred"][s],
                "Pressure (bar)": r["pres_pred"][s],
                "Status": r["status"][s],
            })
    return pd.DataFrame(rows)