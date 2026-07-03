import pandas as pd
import numpy as np

PATH_CSV = '../raw_dataset.csv'

def preprocessing_data(df):
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
    
    return df

if __name__ == "__main__":
    print(preprocessing_data(PATH_CSV))