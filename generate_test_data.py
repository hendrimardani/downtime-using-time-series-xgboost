import pandas as pd
import numpy as np

# Load raw data and filter M003
df = pd.read_csv('raw_dataset.csv')
m3 = df[df['machine_id'] == 'M003'].copy()
m3['timestamp'] = pd.to_datetime(m3['timestamp'], format='mixed')
m3 = m3.sort_values('timestamp').reset_index(drop=True)

# Get the last row values to continue from
last_row = m3.iloc[-1]
last_ts = last_row['timestamp']   # 2024-12-31 23:55:00
last_op_hours = last_row['operating_hours']  # 4018.72

# Use the last 1 hour of RUNNING data (13 rows) as the pattern seed
ref = m3.tail(13)
ref_temps = ref['temperature_C'].values
ref_vibs = ref['vibration_mm_s'].values
ref_pres = ref['pressure_bar'].values

# Generate 12 rows (5-min intervals for 1 hour)
np.random.seed(42)
n_rows = 12
rows = []

for i in range(n_rows):
    ts = last_ts + pd.Timedelta(minutes=5 * (i + 1))

    # Use pattern from last-hour reference + small gaussian noise
    idx = i % len(ref_temps)
    temp = round(np.clip(ref_temps[idx] + np.random.normal(0, 0.5), 14.5, 97.84), 2)
    vib  = round(np.clip(ref_vibs[idx]  + np.random.normal(0, 0.15), 0.0, 6.25), 3)
    pres = round(np.clip(ref_pres[idx]  + np.random.normal(0, 0.08), 0.0, 5.94), 2)

    op_hours = round(last_op_hours + 0.08 * (i + 1), 2)

    # Shift based on hour
    hour = ts.hour
    if 6 <= hour < 14:
        shift = 'Day_Shift'
    elif 14 <= hour < 22:
        shift = 'Evening_Shift'
    else:
        shift = 'Night_Break'

    prod   = int(np.random.choice([5, 6, 7], p=[0.4, 0.35, 0.25]))
    defect = int(np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2]))
    good   = max(prod - defect, 0)

    rows.append({
        'timestamp': ts.strftime('%d/%m/%Y %H:%M'),
        'machine_id': 'M003',
        'temperature_C': temp,
        'vibration_mm_s': vib,
        'pressure_bar': pres,
        'status': 'RUNNING',
        'operating_hours': op_hours,
        'ambient_temp_C': 15.0,
        'shift': shift,
        'production_count': prod,
        'defect_count': defect,
        'good_count': good,
    })

df_test = pd.DataFrame(rows)
df_test.to_csv('test_data_future.csv', index=False)

print("=== test_data_future.csv ===")
print(f"Rows: {len(df_test)}")
print(f"Time: {rows[0]['timestamp']}  ->  {rows[-1]['timestamp']}")
print()
print(df_test.to_string(index=False))
