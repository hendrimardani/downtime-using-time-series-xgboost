# Time Series Prediction Dashboard (XGBoost)

Proyek ini adalah sebuah *dashboard* interaktif berbasis web (menggunakan Streamlit) untuk memprediksi data sensor *time series* hingga 24 step (jam) ke depan menggunakan model Machine Learning **XGBoost**. Aplikasi ini dirancang dengan antarmuka (UI) bernuansa *dark mode* yang elegan dan interaktif.

## Fitur Utama
- **Prediksi Otomatis 24-Step**: Memprediksi 3 parameter sensor (Suhu, Getaran, Tekanan) secara bersamaan untuk 24 step ke depan.
- **Deteksi Risiko (Risk Assessment)**: Otomatis mengklasifikasikan kondisi mesin ke dalam status 🟢 Aman, 🟡 Waspada, atau 🔴 Bahaya berdasarkan nilai maksimal prediksi masing-masing parameter.
- **Visualisasi Interaktif**: Menggunakan Plotly untuk memvisualisasikan tren sensor, korelasi (*heatmap*), dan sebaran risiko (grafik *donut* dan *bar*).
- **Ekspor Data**: Menyediakan fitur untuk mengunduh hasil prediksi 24-step dalam bentuk CSV.

## Input (Masukan)
Aplikasi menerima input berupa file **CSV** dengan kolom-kolom *lag features* (historis) sebagai berikut:
- `temperature_lag1`, `temperature_lag24`
- `vibration_lag1`, `vibration_lag24`
- `pressure_bar_lag1`, `pressure_bar_lag24`

*Catatan: Aplikasi memiliki fitur auto-detect yang dapat menyesuaikan penamaan kolom yang bervariasi (misal: `suhu_lag1`, `temp_lag_1`, `tekanan_lag24`, dll) agar sesuai format standar.*

## Output (Keluaran)
- **Ringkasan Keseluruhan**: Menampilkan persentase jumlah data yang masuk ke kategori aman, waspada, atau bahaya.
- **Tabel Ringkasan**: Merangkum nilai rata-rata dan maksimum prediksi untuk setiap baris data input.
- **Grafik Detail per Data**: Menampilkan overlay perbandingan prediksi tiap fitur, grafik korelasi antar fitur, serta plot pergerakan untuk 24 step ke depan.
- **File CSV Prediksi**: Dapat diunduh oleh pengguna yang berisi seluruh *time series* prediksi dari step 1 hingga 24.

## Teknologi yang Digunakan
Proyek ini dibangun menggunakan teknologi berikut:
- **Python** (Bahasa Pemrograman Utama)
- **Streamlit** (Framework untuk pembuatan UI/Dashboard interaktif)
- **XGBoost** (Algoritma Machine Learning untuk regresi berantai / *chain model*)
- **Pandas & NumPy** (Manipulasi dan perhitungan matriks data)
- **Plotly** (Visualisasi grafik interaktif & responsif)
- **Joblib** (Untuk *loading* pretrained ML model)

## Cara Menjalankan Aplikasi

1. Pastikan Anda telah menginstal **Python 3.9+** di komputer Anda.
2. (*Opsional namun direkomendasikan*) Buat virtual environment terlebih dahulu:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # (Untuk Windows)
   ```
3. Install seluruh paket/library yang dibutuhkan. Buka terminal dan jalankan:
   ```bash
   pip install streamlit pandas numpy plotly xgboost scikit-learn
   ```
4. Masuk ke direktori proyek ini dan jalankan aplikasi Streamlit:
   ```bash
   streamlit run dashboard.py
   ```
5. Aplikasi akan otomatis terbuka di browser web (secara default di `http://localhost:8501`).
