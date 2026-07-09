## 📋 Daftar Isi

- [Deskripsi Proyek](#deskripsi-proyek)
- [Fitur Utama](#fitur-utama)
- [Informasi Dataset (Dataset Mentah)](#informasi-dataset-dataset-mentah)
- [Input (Masukan)](#input-masukan)
- [Output (Keluaran)](#output-keluaran)
- [Model Machine Learning](#model-machine-learning)
- [Klasifikasi Status Mesin](#klasifikasi-status-mesin)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Cara Menjalankan Aplikasi](#cara-menjalankan-aplikasi)
- [Cara Menggunakan Dashboard](#cara-menggunakan-dashboard)
- [Struktur Proyek](#struktur-proyek)

---

## Deskripsi Proyek

Proyek ini adalah sebuah aplikasi web interaktif yang dibangun menggunakan framework streamlit dirancang untuk membantu operator dan teknisi dalam memantau dan memprediksi kondisi mesin industri secara proaktif. Sistem menerima data historis sensor mesin sebagai input, kemudian menggunakan model machine learning yang telah dilatih untuk memperkirakan kondisi mesin 24 jam ke depan dan  mengklasifikasikannya ke dalam tiga status kategori risiko: **aman**, **waspada**, dan **bahaya**. Dashboard interaktif dibangun menggunakan streamlit dengan fitur:

- Prediksi multi-step 24 jam untuk 3 parameter sensor secara simultan
- Klasifikasi risiko otomatis (Aman / Waspada / Bahaya) berdasarkan ambang batas statistik dari data historis
- Visualisasi interaktif menggunakan Plotly (grafik forecast detail & overlay)
- Batch prediction dengan dukungan upload CSV & ekspor hasil (CSV/JSON)
- Auto-refresh & logging untuk monitoring real-time
- UI modern dengan dark-mode & glassmorphism styling

**Tech Stack**: Python, Streamlit, XGBoost, Scikit-learn (RegressorChain), Pandas, Plotly, Joblib

---

## Fitur Utama

| Fitur | Deskripsi |
|:---|:---|
| 🔮 **Prediksi 24-Step** | Memprediksi 3 parameter sensor (suhu, getaran, tekanan) secara bersamaan untuk 24 langkah (jam) ke depan |
| 🚦 **Deteksi Status Risiko** | Mengklasifikasikan tiap prediksi ke dalam status 🟢 aman, 🟡 waspada, atau 🔴 bahaya secara otomatis |
| 📊 **Visualisasi Interaktif** | Grafik detail 24-step dan grafik overlay semua fitur menggunakan Plotly |
| 🔄 **Auto Refresh** | Halaman dapat diatur agar otomatis menyegarkan data setiap 1 menit, 1 jam, atau 1 hari |
| ⏱️ **Countdown Timer** | Menampilkan waktu mundur dan progress bar hingga refresh berikutnya |
| 📥 **Template CSV** | Menyediakan template CSV yang dapat diunduh sebagai panduan format input |
| 📤 **Ekspor Hasil** | Mengunduh seluruh hasil prediksi dalam format **CSV** atau **JSON** |
| 📋 **Tabel Prediksi** | Tabel detail dengan pewarnaan status per baris prediksi |
| 📊 **Ringkasan Batch** | Menampilkan jumlah dan persentase data yang berstatus Aman, Waspada, dan Bahaya |
| 📝 **Logging Tracking** | Menampilkan informasi logging eksekusi autorefresh dan script di background |

## Informasi Dataset (Dataset Mentah)

### Deskripsi Dataset

Dataset ini menyajikan gambaran terstruktur mengenai pemantauan mesin industri untuk pemeliharaan prediktif dan analisis manufaktur cerdas. Dataset ini menggabungkan pembacaan sensor, kejadian kegagalan mesin, dan catatan pemeliharaan dalam tiga berkas CSV.

| Fitur | Deskripsi |
|:---|:---|
| 🕒 **timestamp** | Tanggal dan waktu ketika pembacaan sensor dicatat |
| ⚙️ **machine_id** | Pengidentifikasi unik dari mesin yang dipantau |
| 🌡️ **temperature_C** | Suhu mesin diukur dalam derajat Celcius |
| 📳 **vibration_mm_s** | Tingkat getaran mesin diukur dalam milimeter per detik |
| 🔧 **pressure_bar** | Tingkat tekanan mesin yang diukur dalam bar |
| 🚦 **status** | Status operasi mesin saat ini, seperti sedang berjalan atau berhenti |
| ⌛ **operating_hours** | Total waktu pengoperasian mesin yang telah terakumulasi |
| 🌡️ **ambient_temp_C** | Suhu lingkungan di sekitar mesin dalam derajat Celcius |
| 🌓 **shift** | Shift kerja saat pembacaan sensor tersebut dicatat |
| 📦 **production_count** | Jumlah total unit yang diproduksi selama periode yang dicatat |
| ❌ **defect_count** | Jumlah unit cacat yang diproduksi selama periode yang dicatat |
| ✅ **good_count** | Jumlah unit berkualitas baik yang diproduksi selama periode yang dicatat |

Tautan dataset: https://www.kaggle.com/datasets/harrachimustapha/maintenance-machine?select=sensor_data.csv

## Input (Masukan)

Aplikasi menerima input berupa file **CSV** yang diunggah melalui sidebar. File harus memiliki **8 kolom** berikut:

| No | Nama Kolom | Tipe Data | Deskripsi |
|:--:|:---|:---:|:---|
| 1 | `temperature_C_lag_1` | `float` | Suhu mesin (°C) pada 1 jam sebelumnya |
| 2 | `temperature_C_lag_24` | `float` | Suhu mesin (°C) pada 24 jam sebelumnya |
| 3 | `vibration_mm_s_lag_1` | `float` | Getaran mesin (mm/s) pada 1 jam sebelumnya |
| 4 | `vibration_mm_s_lag_24` | `float` | Getaran mesin (mm/s) pada 24 jam sebelumnya |
| 5 | `pressure_bar_lag_1` | `float` | Tekanan mesin (bar) pada 1 jam sebelumnya |
| 6 | `pressure_bar_lag_24` | `float` | Tekanan mesin (bar) pada 24 jam sebelumnya |
| 7 | `day_of_week` | `int` | Hari dalam seminggu (`0` = Senin, `6` = Minggu) |
| 8 | `is_holiday` | `int` | Indikator hari libur (`1` = libur, `0` = hari kerja) |

> **Catatan:** Setiap baris pada CSV merepresentasikan satu titik waktu dan akan menghasilkan prediksi 24 langkah ke depan.

### Contoh Format CSV

| `temperature_C_lag_1` | `temperature_C_lag_24` | `vibration_mm_s_lag_1` | `vibration_mm_s_lag_24` | `pressure_bar_lag_1` | `pressure_bar_lag_24` | `day_of_week` | `is_holiday` |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 25.0 | 24.5 | 0.004 | 0.0038 | 2.0 | 1.8 | 0 | 0 |

Template CSV dapat diunduh langsung dari dalam dashboard melalui sidebar → **Format CSV yang Diharapkan** → tombol **Download Template CSV**.

### Cara Mendapatkan Data Input

Jika Anda memiliki data mentah sensor mesin (seperti `raw_dataset.csv`), gunakan fungsi preprocessing yang tersedia di `utils/preprocessing.py` untuk menghasilkan file CSV yang siap diinput ke dashboard:

```python
from utils.preprocessing import preprocessing_data
preprocessing_data('path/ke/raw_dataset.csv')
# Menghasilkan file preprocessed_dataset.csv
```

---

## Output (Keluaran)

### 1. 📊 Grafik Prediksi (Tab "Grafik Detail")

- **Grafik Prediksi 24-Step**: Grafik garis terpisah untuk suhu (Temperature °C), getaran (Vibration mm/s), dan tekanan (Pressure bar) selama 24 jam ke depan.
- **Grafik Overlay Semua Fitur**: Grafik yang menampilkan ketiga fitur dalam satu tampilan untuk melihat pola bersama (*combined chart*).

### 2. 📋 Tabel Prediksi (Tab "Tabel")

Tabel berisi 24 baris prediksi dengan kolom:

| Kolom | Keterangan |
|:---|:---|
| `Datetime` | Tanggal dan waktu prediksi (per jam) |
| `Temperature (°C)` | Nilai prediksi suhu |
| `Vibration (mm/s)` | Nilai prediksi getaran |
| `Pressure (bar)` | Nilai prediksi tekanan |
| `Status` | Klasifikasi risiko: `aman`, `waspada`, atau `bahaya` |

### 3. 📈 Ringkasan Seluruh Prediksi

Menampilkan 4 kartu KPI:
- Jumlah prediksi berstatus 🟢 **Aman**
- Jumlah prediksi berstatus 🟡 **Waspada**
- Jumlah prediksi berstatus 🔴 **Bahaya**
- **Tingkat Aman** (persentase)

### 4. 💾 File yang Dapat Diunduh

| Format | Nama File | Isi |
|:---|:---|:---|
| **CSV** | `prediksi_downtime_all.csv` | Seluruh prediksi 24 langkah dari semua baris data input |
| **JSON** | `prediksi_downtime_all.json` | Sama seperti CSV, dalam format JSON (array of records) |

Struktur kolom file ekspor: `Datetime`, `step`, `Temperature (°C)`, `Vibration (mm/s)`, `Pressure (bar)`, `Status`.

---

## Model Machine Learning

| Parameter | Nilai |
|:---|:---|
| **Algoritma** | XGBoost + Scikit-learn `RegressorChain` |
| **File Model** | `xgboost_chain_model_24h.joblib` |
| **Fitur Input** | 8 kolom (6 lag features + 2 fitur temporal) |
| **Horizon Prediksi** | 24 langkah ke depan (24 jam) |
| **Variabel Target** | 3 variabel × 24 langkah = **72 nilai output** per baris |
| **Mode Inferensi** | Batch (dapat memproses banyak baris sekaligus) |

### Target Output Model

Model memprediksi 72 nilai sekaligus dalam format:
```
temperature_C_t_1, vibration_mm_s_t_1, pressure_bar_t_1,
temperature_C_t_2, vibration_mm_s_t_2, pressure_bar_t_2,
...
temperature_C_t_24, vibration_mm_s_t_24, pressure_bar_t_24
```

---

## Klasifikasi Status Mesin

Status setiap langkah prediksi ditentukan berdasarkan ambang batas statistik yang diturunkan dari data historis:

### 🟢 Aman (Normal)

Kondisi mesin beroperasi normal. Nilai prediksi berada dalam rentang berikut:

| Parameter | Batas Bawah | Batas Atas |
|:---|:---:|:---:|
| Temperature (°C) | 70.63 | 77.65 |
| Vibration (mm/s) | 3.236 | 4.680 |
| Pressure (bar) | 4.780 | 5.140 |

### 🟡 Waspada (Peringatan)

Nilai prediksi berada di luar zona normal namun belum mencapai zona bahaya (nilai di antara ambang batas Normal dan Downtime).

### 🔴 Bahaya (Downtime)

Kondisi kritis yang mengindikasikan potensi *downtime*. Nilai prediksi berada dalam rentang berikut:

| Parameter | Batas Bawah | Batas Atas |
|:---|:---:|:---:|
| Temperature (°C) | 15.99 | 22.46 |
| Vibration (mm/s) | 0.008 | 0.023 |
| Pressure (bar) | 0.010 | 0.040 |

> **Logika Klasifikasi:** Status "Bahaya" diberikan hanya jika **ketiga** parameter sekaligus berada di zona bahaya. Jika hanya sebagian yang di luar normal, statusnya adalah "Waspada".

---

## Teknologi yang Digunakan

| Library | Versi | Fungsi |
|:---|:---:|:---|
| **Python** | 3.9+ | Bahasa pemrograman utama |
| **Streamlit** | 1.58.0 | Framework dashboard web interaktif |
| **streamlit-autorefresh** | 1.0.1 | Fitur auto refresh halaman |
| **XGBoost** | 3.3.0 | Algoritma ML untuk prediksi *time series* |
| **Scikit-learn** | 1.6.1 | `RegressorChain` untuk prediksi multi-output berantai |
| **Pandas** | 2.3.3 | Manipulasi dan analisis data tabular |
| **Plotly** | 6.8.0 | Visualisasi grafik interaktif |
| **Joblib** | 1.5.3 | Memuat model ML dari file `.joblib` |

---

## Cara Menjalankan Aplikasi

### Prasyarat

- Python **3.9** atau lebih baru
- Git (opsional)

### Langkah Instalasi

**1. Clone atau unduh repositori ini:**
```bash
git clone https://github.com/hendrimardani/downtime-using-time-series-xgboost.git
cd "downtime-using-time-series-xgboost"
```

**2. (Direkomendasikan) Buat virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install seluruh dependensi:**
```bash
pip install -r requirements.txt
```

**4. Jalankan aplikasi Streamlit:**
```bash
streamlit run dashboard.py
```

**5.** Aplikasi akan otomatis terbuka di browser pada alamat `http://localhost:8501`.

---

## Cara Menggunakan Dashboard

1. **Buka aplikasi** di browser setelah menjalankan perintah di atas.
2. Masuk ke folder **utils** kemudian jalankan dengan perintah ```python preprocessing.py``` tujuannya membuat berkas bernama **preprocessed_dataset.csv** yang nantinya akan digunakan untuk input fitur yang dibutuhkan oleh model saat inferensi.
2. **Atur Auto Refresh** (opsional) melalui dropdown di sidebar — pilih interval: nonaktif, 1 menit, 1 jam, atau 1 hari.
3. **Upload file CSV** yang baru saja dibuat hasil preprocessing data yang bernama **preprocessed_dataset.csv** melalui tombol *file uploader* di sidebar. Pastikan format sesuai dengan 8 kolom yang dibutuhkan.
4. Setelah file diunggah, dashboard secara otomatis:
   - Menampilkan **preview data input** beserta jumlah baris dan kolom.
   - Menjalankan **prediksi** menggunakan model XGBoost.
   - Menampilkan **ambang batas statistik** untuk kategori Aman, Waspada, dan Bahaya.
   - Menampilkan **detail prediksi** dalam bentuk grafik dan tabel.
   - Menampilkan **ringkasan batch** seluruh prediksi.
5. Gunakan **slider** (jika data lebih dari 1 baris) untuk berpindah antar-detail prediksi.
6. **Unduh hasil** prediksi dalam format CSV atau JSON dari bagian bawah halaman.

---

## Struktur Proyek

```
Downtime using Time Series XGBoost-RegressionChain/
├── 📄 dashboard.py                    # Aplikasi utama Streamlit
├── 📄 requirements.txt                # Dependensi Python
├── 📄 generate_test_data.py           # Generator data uji dari raw_dataset.csv
├── 📊 raw_dataset.csv                 # Dataset mentah sensor mesin
├── 📊 test_data_future.csv            # Contoh data uji yang digenerate
├── 🤖 xgboost_chain_model_24h.joblib  # Pre-trained model XGBoost
│
|── 📁 logging/                       # Logging
│   ├── autorefresh.csv                # Logging untuk autorefresh
│   └── preprocessing_script.csv       # Logging untuk script di background
|
├── 📁 ui/
│   ├── __init__.py                    # Ekspor fungsi UI
│   ├── styles.py                      # CSS dark-mode & glassmorphism
│   ├── components.py                  # Komponen Streamlit (header, card, dll.)
│   └── charts.py                      # Grafik Plotly (forecast & combined)
│
└── 📁 utils/
    ├── __init__.py                    # Ekspor fungsi utils
    ├── data.py                        # Konstanta FEATURES, TARGETS, HORIZON
    ├── model.py                       # Load model & run_prediction()
    └── preprocessing.py               # Ambang batas & status_downtime()
```

**Tautan Demo:** [Demo](https://bit.ly/demo_downtime_using_xgboost_regression_chain)
