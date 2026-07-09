import pandas as pd
import os
import sys
from pathlib import Path

try:
    from utils.data import export_logging_df
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from utils.data import export_logging_df

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INPUT_RAW_DATASET =f"{BASE_DIR}/raw_dataset.csv"
OUTPUT_DATA_PREPROCESSING = f"{BASE_DIR}/preprocessed_dataset.csv"

FOLDER_LOGGING = os.path.join(BASE_DIR, "logging")
OUTPUT_LOGGING_SCRIPT = os.path.join(FOLDER_LOGGING, "preprocessing_script.csv")

if not os.path.exists(FOLDER_LOGGING):
    os.makedirs(FOLDER_LOGGING, exist_ok=True)

# Normal
LOWER_TEMP_NORMAL = 70.630000
LOWER_VIB_NORMAL = 3.236000
LOWER_PRESS_NORMAL = 4.780000

UPPER_TEMP_NORMAL = 77.650000
UPPER_VIB_NORMAL = 4.680000
UPPER_PRESS_NORMAL = 5.140000

# Bahaya
LOWER_TEMP_DOWNTIME = 15.990000
LOWER_VIB_DOWNTIME = 0.008000
LOWER_PRESS_DOWNTIME = 0.010000

UPPER_TEMP_DOWNTIME = 22.460000
UPPER_VIB_DOWNTIME = 0.023000
UPPER_PRESS_DOWNTIME = 0.040000


def preprocessing_data(df):
    status = None
    try:
        df = pd.read_csv(df)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
        df.set_index('timestamp', inplace=True)
        df.drop(['machine_id', 'shift', 'operating_hours', 'status', 'ambient_temp_C', 'production_count', 'defect_count', 'good_count'], axis=1, inplace=True)

        agg_rules = {
            'temperature_C': ['mean', 'max', 'min', 'std'],
            'vibration_mm_s': ['mean', 'max', 'min', 'std'],
            'pressure_bar': ['mean', 'max', 'min', 'std']
        }
        df = df.resample('1H').agg(agg_rules)

        df = df[[("temperature_C", "mean"), ("vibration_mm_s", "mean"), ("pressure_bar", "mean")]]
        df.columns = [
            "temperature_C_mean",
            "vibration_mm_s_mean",
            "pressure_bar_mean"
        ]

        df.rename({
        'temperature_C_mean': 'temperature_C',
        'vibration_mm_s_mean': 'vibration_mm_s',
        'pressure_bar_mean': 'pressure_bar'
        }, axis=1, inplace=True)

        df["temperature_C_lag_1"] = df["temperature_C"].shift(1)
        df["temperature_C_lag_24"] = df["temperature_C"].shift(24)
        df["vibration_mm_s_lag_1"] = df["vibration_mm_s"].shift(1)
        df["vibration_mm_s_lag_24"] = df["vibration_mm_s"].shift(24)
        df["pressure_bar_lag_1"] = df["pressure_bar"].shift(1)
        df["pressure_bar_lag_24"] = df["pressure_bar"].shift(24)
        df = df.dropna()
        
        df.reset_index("timestamp", inplace=True)
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["is_holiday"] = df["timestamp"].dt.dayofweek >= 5
        df["is_holiday"] = df["is_holiday"].map(lambda x: 1 if x else 0)
        last_row = df.iloc[-1, :].to_frame().T

        features = [
            feature
                for feature in last_row.columns
                    if feature.endswith('lag_1') or feature.endswith('lag_24') 
                        or feature in ['timestamp', 'day_of_week', 'is_holiday']
            ]
        last_row = last_row[features]
        last_row.to_csv(OUTPUT_DATA_PREPROCESSING, index=False)
        status = "berhasil"
    except Exception as e:
        print(f"Error logging script: ", e)
        status = "gagal"

    export_logging_df(OUTPUT_LOGGING_SCRIPT, status)

def status_downtime(row):
    is_threshold_temp_normal = LOWER_TEMP_NORMAL <= row['temperature_C_pred'] <= UPPER_TEMP_NORMAL
    is_threshold_vib_normal = LOWER_VIB_NORMAL <= row['vibration_mm_s_pred'] <= UPPER_VIB_NORMAL
    is_threshold_pres_normal = LOWER_PRESS_NORMAL <= row['pressure_bar_pred'] <= UPPER_PRESS_NORMAL

    if not is_threshold_temp_normal and not is_threshold_vib_normal and not is_threshold_pres_normal:
        is_threshold_temp_downtime = LOWER_TEMP_DOWNTIME <= row['temperature_C_pred'] <= UPPER_TEMP_DOWNTIME
        is_threshold_vib_downtime = LOWER_VIB_DOWNTIME <= row['vibration_mm_s_pred'] <= UPPER_VIB_DOWNTIME
        is_threshold_press_downtime = LOWER_PRESS_DOWNTIME <= row['pressure_bar_pred'] <= UPPER_PRESS_DOWNTIME

        if is_threshold_temp_downtime and is_threshold_vib_downtime and is_threshold_press_downtime:
            return 'bahaya'
        return 'waspada'
    else:
        return 'aman'


if __name__ == "__main__":
    preprocessing_data(INPUT_RAW_DATASET)
