import streamlit as st
import pandas as pd
from utils.data import create_export_dataframe
from ui import (
    inject_css,
    color_status,
    render_header,
    render_kpi_row,
    render_section_header,
    render_welcome_page,
    render_footer,
    render_alert,
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
    LOWER_TEMP_NORMAL, LOWER_VIB_NORMAL, LOWER_PRESS_NORMAL,
    UPPER_TEMP_NORMAL, UPPER_VIB_NORMAL, UPPER_PRESS_NORMAL,
    LOWER_TEMP_DOWNTIME, LOWER_VIB_DOWNTIME, LOWER_PRESS_DOWNTIME,
    UPPER_TEMP_DOWNTIME, UPPER_VIB_DOWNTIME, UPPER_PRESS_DOWNTIME
)

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
    st.markdown("## 📂 Upload Data CSV")
    st.markdown(
        "Upload file CSV berisi data lag fitur mesin. "
        "Setiap baris akan diprediksi **24 step ke depan**."
    )

    uploaded_file = st.file_uploader(
        "Pilih file CSV",
        type=["csv"],
        help="File CSV dengan kolom lag-1 dan lag-24 untuk temperature, vibration, dan pressure_bar",
    )
    st.markdown("---")

    with st.expander("ℹ️ Format CSV yang Diharapkan", expanded=False):
        st.markdown("""
        File CSV harus memiliki **6 kolom** berikut:

        | Kolom | Keterangan |
        |-------|------------|
        | `temperature_C_lag_1` | Suhu lag-1 |
        | `temperature_C_lag_24` | Suhu lag-24 |
        | `vibration_mm_s_lag_1` | Getaran lag-1 |
        | `vibration_mm_s_lag_24` | Getaran lag-24 |
        | `pressure_bar_lag_1` | Tekanan lag-1 |
        | `pressure_bar_lag_24` | Tekanan lag-24 |
        | `day_of_week` | Hari dalam minggu (0=Senin, 6=Minggu) |
        | `is_holiday` | 1 jika hari libur, 0 jika hari kerja |
                    
        Setiap **baris** = satu input prediksi.
        """)

        template_df = pd.DataFrame({
            "temperature_C_lag_1": [25.0],
            "temperature_C_lag_24": [24.5],
            "vibration_mm_s_lag_1": [0.0040],
            "vibration_mm_s_lag_24": [0.0038],
            "pressure_bar_lag_1": [2.0],
            "pressure_bar_lag_24": [1.8],
            "day_of_week": [0],
            "is_holiday": [0],
        })
        st.download_button(
            label="📥 Download Template CSV",
            data=template_df.to_csv(index=False).encode("utf-8"),
            file_name="template_input_prediksi.csv",
            mime="text/csv",
            use_container_width=True,
        )

if not model_loaded:
    st.error(f"❌ Gagal memuat model: `{model_error}`")
    st.info("Pastikan file `xgboost_chain_model_24h.joblib` berada di direktori yang sama dengan `dashboard.py`.")
    st.stop()


if uploaded_file is not None:
    try:
        df_input = pd.read_csv(uploaded_file)
        filename = uploaded_file.name
        datetime_format = filename.split("_")[:5]
        date_string = "_".join(datetime_format)
        last_time = pd.to_datetime(date_string, format="%Y_%m_%d_%H_%M")
    except Exception as e:
        st.error(f"❌ Gagal membaca file CSV: {e}")
        st.stop()

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
        df_datetime = df_features.copy()
        df_datetime["timestamp"] = last_time
        new_sort_features = [
            "timestamp", "temperature_C_lag_1", "temperature_C_lag_24",
            "vibration_mm_s_lag_1", "vibration_mm_s_lag_24",
            "pressure_bar_lag_1", "pressure_bar_lag_24",
            "day_of_week", "is_holiday"
        ]
        df_datetime = df_datetime[new_sort_features]
        st.dataframe(df_datetime, use_container_width=True, height=300)

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
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼🌡️ Batas Atas (Temperature C)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{UPPER_TEMP_NORMAL}</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼📳 Batas Atas (Vibration mm/s)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{UPPER_VIB_NORMAL}</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼🔧 Batas Atas (Pressure bar)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{UPPER_PRESS_NORMAL}</div>
        </div>
        """, unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Temperature C)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{LOWER_TEMP_NORMAL}</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Vibration mm/s)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{LOWER_VIB_NORMAL}</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Pressure bar)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{LOWER_PRESS_NORMAL}</div>
        </div>
        """, unsafe_allow_html=True)
    

    # ── Threshold Waspada ───────────────────────────────────────────
    render_section_header("🟡 Kategori Waspada Ambang Batas Statistik")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼🌡️ Batas Atas (Temperature C)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">[{UPPER_TEMP_DOWNTIME} - {UPPER_TEMP_NORMAL}]</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼📳 Batas Atas (Vibration mm/s)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">[{UPPER_VIB_DOWNTIME} - {UPPER_VIB_NORMAL}]</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼🔧 Batas Atas (Pressure bar)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">[{UPPER_PRESS_DOWNTIME} - {UPPER_PRESS_NORMAL}]</div>
        </div>
        """, unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Temperature C)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">[{LOWER_TEMP_DOWNTIME} - {LOWER_TEMP_NORMAL}]</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Vibration mm/s)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">[{LOWER_VIB_DOWNTIME} - {LOWER_VIB_NORMAL}]</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Pressure bar)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">[{LOWER_PRESS_DOWNTIME} - {LOWER_PRESS_NORMAL}]</div>
        </div>
        """, unsafe_allow_html=True)


    # ── Threshold Bahaya ───────────────────────────────────────────
    render_section_header("🔴 Kategori Bahaya Ambang Batas Statistik")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼🌡️ Batas Atas (Temperature C)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{UPPER_TEMP_DOWNTIME}</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼📳 Batas Atas (Vibration mm/s)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{UPPER_VIB_DOWNTIME}</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔼🔧 Batas Atas (Pressure bar)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{UPPER_PRESS_DOWNTIME}</div>
        </div>
        """, unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Temperature C)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{LOWER_TEMP_DOWNTIME}</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Vibration mm/s)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{LOWER_VIB_DOWNTIME}</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔽🌡️ Batas Bawah (Pressure bar)</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{LOWER_PRESS_DOWNTIME}</div>
        </div>
        """, unsafe_allow_html=True)


    # ── Detail Prediksi ──────────────────────────────────────────────
    render_section_header("🔍 Detail Prediksi")
    if n_rows > 1:
        selected_row = st.slider(
            "Pilih data ke-", min_value=1, max_value=n_rows, value=1, step=1,
            help="Geser untuk melihat detail prediksi setiap baris data",
        )
    else:
        st.info("Hanya 1 data yang tersedia untuk dilihat detailnya.")
        selected_row = 1

    r = all_results[selected_row - 1]

    # ── Tab: Detail ────────────────────────────────────────
    tab_charts, tab_table = st.tabs(["📈 Grafik Detail", "📋 Tabel"])
    with tab_charts:
        st.markdown(f"#### 📈 Grafik Prediksi 24-Step")
        fig_detail = create_forecast_chart(r["time_future"], r["temp_pred"], r["vib_pred"], r["pres_pred"])
        st.plotly_chart(fig_detail, use_container_width=True, key="detail_forecast", theme=None)

        st.markdown("---")

        st.markdown("#### 🔀 Overlay Semua Fitur")
        fig_comb = create_combined_chart(r["time_future"], r["temp_pred"], r["vib_pred"], r["pres_pred"])
        st.plotly_chart(fig_comb, use_container_width=True, key="detail_combined", theme=None)

    with tab_table:
        st.markdown(f"#### 📋 Tabel Detail Prediksi")

        df_detail = pd.DataFrame({
            "Datetime": r["time_future"],
            "Temperature (°C)": r["temp_pred"],
            "Vibration (mm/s)": r["vib_pred"],
            "Pressure (bar)": r["pres_pred"],
            "Status": r["status"],
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
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🟢 Aman</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{sum_aman}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🟡 Waspada</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{sum_waspada}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔴 Bahaya</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{sum_bahaya}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)
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
        st.download_button(
            label="📥 Download CSV",
            data=df_export.to_csv(index=False).encode("utf-8"),
            file_name="prediksi_downtime_all.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            label="📥 Download JSON",
            data=df_export.to_json(orient="records", indent=2).encode("utf-8"),
            file_name="prediksi_downtime_all.json",
            mime="application/json",
            use_container_width=True,
        )
else:
    render_welcome_page()

# Footer
st.markdown("---")
render_footer()
