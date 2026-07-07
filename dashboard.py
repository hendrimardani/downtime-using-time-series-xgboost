import os
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data import create_export_dataframe
from ui import (
    inject_css,
    color_status,
    render_header,
    render_kpi_row,
    render_section_header,
    render_welcome_page,
    render_autorefresh,
    render_upload_data,
    render_kpi_statistics,
    render_kpi_summary,
    render_download_button,
    render_footer,
    render_alert,
    render_task_scheduler_tutorial,
    create_forecast_chart,
    create_combined_chart
)
from utils import (
    load_model,
    run_prediction,
    FEATURES,
    TARGETS,
    HORIZON,
)
from utils.preprocessing import (
    LOWER_TEMP_NORMAL,
    LOWER_VIB_NORMAL,
    LOWER_PRESS_NORMAL,
    UPPER_TEMP_NORMAL,
    UPPER_VIB_NORMAL,
    UPPER_PRESS_NORMAL,
    LOWER_TEMP_DOWNTIME,
    LOWER_VIB_DOWNTIME,
    LOWER_PRESS_DOWNTIME,
    UPPER_TEMP_DOWNTIME,
    UPPER_VIB_DOWNTIME,
    UPPER_PRESS_DOWNTIME
)

output_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PREDIKSI_CSV = f'{output_timestamp}.csv'
OUTPUT_PREDIKSI_JSON = f'{output_timestamp}.json'

st.set_page_config(
    page_title="Prediksi Downtime Mesin",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS & Header
inject_css()
render_header()
st.markdown("---")

try:
    model = load_model()
    model_loaded = True
except Exception as e:
    model_loaded = False
    model_error = str(e)


with st.sidebar:
    render_autorefresh("## 🔄 Auto Refresh")
    uploaded_file = render_upload_data("## 📂 Upload Data CSV")
    render_task_scheduler_tutorial("## 📅 Automasi Script")

if not model_loaded:
    st.error(f"❌ Gagal memuat model: `{model_error}`")
    st.info("Pastikan file `xgboost_chain_model_24h.joblib` berada di direktori yang sama dengan `dashboard.py`.")
    st.stop()

data_available = False
if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    if st.session_state.get("last_uploaded_file") != file_bytes:
        st.session_state["last_uploaded_file"] = file_bytes
        try:
            with open("preprocessed_dataset.csv", "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            st.error(f"Gagal menyimpan file upload: {e}")

    if os.path.exists("preprocessed_dataset.csv"):
        try:
            df_input = pd.read_csv("preprocessed_dataset.csv")
            df_input["timestamp"] = pd.to_datetime(df_input["timestamp"], format="mixed")
            last_time = df_input["timestamp"].iloc[0]
            data_available = True
        except Exception as e:
            st.error(f"❌ Gagal membaca file preprocessed_dataset.csv: {e}")
            st.stop()
    else:
        try:
            df_input = pd.read_csv(uploaded_file)
            df_input["timestamp"] = pd.to_datetime(df_input["timestamp"], format="mixed")
            last_time = df_input["timestamp"].iloc[0]
            data_available = True
        except Exception as e:
            st.error(f"❌ Gagal membaca file CSV: {e}")
            st.stop()
else:
    if "last_uploaded_file" in st.session_state:
        del st.session_state["last_uploaded_file"]
    if os.path.exists("preprocessed_dataset.csv"):
        try:
            os.remove("preprocessed_dataset.csv")
        except:
            pass

if data_available:
    df_features = df_input[FEATURES]
    n_rows = len(df_input)

    # ── Preview Data ──────────────────────────────────────────────
    render_section_header("📂 Preview Data Input")
    render_kpi_row([
        {"icon": "📄", "label": "Total Baris", "value": str(n_rows), "unit": "data input valid"},
        {"icon": "🔢", "label": "Total Kolom", "value": str(len(FEATURES)), "unit": "fitur lag terdeteksi"},
        {"icon": "📊", "label": "Total Prediksi", "value": str(n_rows * 24 * 3), "unit": f"{n_rows} × 24 step × 3 fitur"},
    ])

    with st.expander("👁️ Lihat Data Input", expanded=False):
        st.dataframe(df_input, use_container_width=True, height=300)

    st.markdown("---")

    with st.spinner(f"🔄 Menjalankan prediksi untuk {n_rows} data..."):
        try:
            all_results = run_prediction(model, last_time, df_features.values, TARGETS, HORIZON)
        except Exception as e:
            st.error(f"❌ Error saat prediksi: {e}")
            st.stop()

    render_alert("success", f"✅ <strong>Prediksi berhasil!</strong> {n_rows} baris data telah diprediksi untuk 24 step ke depan.")

    # ── Threshold Normal ───────────────────────────────────────────
    render_section_header("🟢 Kategori Aman Ambang Batas Statistik")
    s1, s2, s3 = st.columns(3)
    with s1:
        render_kpi_statistics("normal", "🔼🌡️ Batas Atas (Temperature C)", UPPER_PRESS_NORMAL)
    with s2:
        render_kpi_statistics("normal", "🔼📳 Batas Atas (Vibration mm/s)", UPPER_VIB_NORMAL)
    with s3:
        render_kpi_statistics("normal", "🔼🔧 Batas Atas (Pressure bar)", UPPER_PRESS_NORMAL)

    s1, s2, s3 = st.columns(3)
    with s1:
        render_kpi_statistics("normal", "🔽🌡️ Batas Bawah (Temperature C)", LOWER_TEMP_NORMAL)
    with s2:
        render_kpi_statistics("normal", "🔽📳 Batas Bawah (Vibration mm/s)", LOWER_VIB_NORMAL)
    with s3:
        render_kpi_statistics("normal", "🔽🔧 Batas Bawah (Pressure bar)", LOWER_PRESS_NORMAL)

    # ── Threshold Waspada ───────────────────────────────────────────
    render_section_header("🟡 Kategori Waspada Ambang Batas Statistik")
    s1, s2, s3 = st.columns(3)
    with s1:
        render_kpi_statistics("waspada", "🔼🌡️ Batas Atas (Temperature C)", UPPER_TEMP_DOWNTIME, UPPER_TEMP_NORMAL)
    with s2:
        render_kpi_statistics("waspada", "🔼📳 Batas Atas (Vibration mm/s)", UPPER_VIB_DOWNTIME, UPPER_VIB_NORMAL)
    with s3:
        render_kpi_statistics("waspada", "🔼🔧 Batas Atas (Pressure bar)", UPPER_PRESS_DOWNTIME, UPPER_PRESS_NORMAL)

    s1, s2, s3 = st.columns(3)
    with s1:
        render_kpi_statistics("waspada", "🔽🌡️ Batas Bawah (Temperature C)", LOWER_TEMP_DOWNTIME, LOWER_TEMP_NORMAL)
    with s2:
        render_kpi_statistics("waspada", "🔽📳  Batas Bawah (Vibration mm/s)", LOWER_VIB_DOWNTIME, LOWER_VIB_NORMAL)
    with s3:
        render_kpi_statistics("waspada", "🔽🔧 Batas Bawah (Pressure bar)", LOWER_PRESS_DOWNTIME, LOWER_PRESS_NORMAL)

    # ── Threshold Bahaya ───────────────────────────────────────────
    render_section_header("🔴 Kategori Bahaya Ambang Batas Statistik")
    s1, s2, s3 = st.columns(3)
    with s1:
        render_kpi_statistics("bahaya", "🔼🌡️ Batas Atas (Temperature C)", UPPER_TEMP_DOWNTIME)
    with s2:
        render_kpi_statistics("bahaya", "🔼📳 Batas Atas (Vibration mm/s)", UPPER_VIB_DOWNTIME)
    with s3:
        render_kpi_statistics("bahaya", "🔼🔧 Batas Atas (Pressure bar)", UPPER_PRESS_DOWNTIME)

    s1, s2, s3 = st.columns(3)
    with s1:
        render_kpi_statistics("bahaya", "🔽🌡️ Batas Bawah (Temperature C)", LOWER_TEMP_DOWNTIME)
    with s2:
        render_kpi_statistics("bahaya", "🔽📳 Batas Bawah (Vibration mm/s)", LOWER_VIB_DOWNTIME)
    with s3:
        render_kpi_statistics("bahaya", "🔽🔧 Batas Bawah (Pressure bar)", LOWER_PRESS_DOWNTIME)

    row_pred = all_results[0]

    # ── Tab: Detail ────────────────────────────────────────
    tab_charts, tab_table = st.tabs(["📈 Grafik Detail", "📋 Tabel"])
    with tab_charts:
        st.markdown(f"#### 📈 Grafik Prediksi 24-Step")
        fig_detail = create_forecast_chart(row_pred["time_future"], row_pred["temp_pred"], row_pred["vib_pred"], row_pred["press_pred"])
        st.plotly_chart(fig_detail, use_container_width=True, key="detail_forecast", theme=None)

        st.markdown("---")

        st.markdown("#### 🔀 Overlay Semua Fitur")
        fig_comb = create_combined_chart(row_pred["time_future"], row_pred["temp_pred"], row_pred["vib_pred"], row_pred["press_pred"])
        st.plotly_chart(fig_comb, use_container_width=True, key="detail_combined", theme=None)

    with tab_table:
        st.markdown(f"#### 📋 Tabel Detail Prediksi")
        df_detail = pd.DataFrame({
            "Datetime": row_pred["time_future"],
            "Temperature (°C)": row_pred["temp_pred"],
            "Vibration (mm/s)": row_pred["vib_pred"],
            "Pressure (bar)": row_pred["press_pred"],
            "Status": row_pred["status"],
        }).set_index("Datetime")
        df_detail_styled = df_detail.style.map(color_status, subset=["Status"])
        st.dataframe(df_detail_styled, use_container_width=True, height=400)

    st.markdown("---")

        # ── Ringkasan Batch ───────────────────────────────────────────
    render_section_header("📊 Ringkasan Seluruh Prediksi")
    sum_aman = len(df_detail[df_detail["Status"] == "aman"])
    sum_waspada = len(df_detail[df_detail["Status"] == "waspada"])
    sum_bahaya = len(df_detail[df_detail["Status"] == "bahaya"])
    n_rows = df_detail.shape[0]

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        render_kpi_summary("normal", "🟢 Aman", sum_aman, n_rows)
    with s2:
        render_kpi_summary("waspada", "🟡 Waspada", sum_waspada, n_rows)
    with s3:
        render_kpi_summary("bahaya", "🔴 Bahaya", sum_bahaya, n_rows)
    with s4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">✅ Tingkat Aman</div>
            <div class="kpi-value">{sum_aman:.1f}%</div>
            <div class="kpi-unit">data dalam batas aman</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Download ────────────────────────────────────────────
    render_section_header("💾 Unduh Hasil Prediksi")
    df_export = create_export_dataframe(all_results)
    dl1, dl2, _ = st.columns([1, 1, 2])

    with dl1:
        render_download_button(df_export, "csv",  OUTPUT_PREDIKSI_CSV)
    with dl2:
        render_download_button(df_export, "json",  OUTPUT_PREDIKSI_JSON)

else:
    render_welcome_page()

# Footer
st.markdown("---")
render_footer()