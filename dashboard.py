import streamlit as st
import pandas as pd
import numpy as np

from ui import (
    inject_css,
    render_header,
    render_kpi_card,
    render_kpi_row,
    render_section_header,
    render_welcome_page,
    render_footer,
    render_alert,
    render_risk_alerts,
    render_input_summary,
    render_prediction_stats,
    create_forecast_chart,
    create_combined_chart,
    create_heatmap_chart,
    create_batch_overview_chart,
    create_risk_donut_chart,
)
from utils import (
    load_model,
    run_prediction,
    auto_detect_columns,
    validate_csv,
    get_risk_status,
    FEATURES,
    TARGETS,
    HORIZON,
)
from utils.data import compute_risk_for_results, create_export_dataframe, create_summary_dataframe

# ──────────────────────────────────────────────────────────────────────
# Konfigurasi halaman
# ──────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prediksi Downtime Mesin",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────
# Inject CSS & Header
# ──────────────────────────────────────────────────────────────────────
inject_css()
render_header()
st.markdown("---")

# ──────────────────────────────────────────────────────────────────────
# Load Model
# ──────────────────────────────────────────────────────────────────────
try:
    model = load_model()
    model_loaded = True
except Exception as e:
    model_loaded = False
    model_error = str(e)

# ──────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────
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

    # --- Threshold Kustomisasi ---
    with st.expander("⚠️ Kustomisasi Threshold Risiko", expanded=False):
        st.markdown("**Temperature (°C)**")
        temp_warn = st.number_input("Warning ≥", value=35.0, step=0.5, key="tw")
        temp_danger = st.number_input("Danger ≥", value=45.0, step=0.5, key="td")

        st.markdown("**Vibration (mm/s)**")
        vib_warn = st.number_input("Warning ≥", value=0.0080, step=0.0001, format="%.4f", key="vw")
        vib_danger = st.number_input("Danger ≥", value=0.0120, step=0.0001, format="%.4f", key="vd")

        st.markdown("**Pressure (bar)**")
        pres_warn = st.number_input("Warning ≥", value=5.0, step=0.5, key="pw")
        pres_danger = st.number_input("Danger ≥", value=8.0, step=0.5, key="pd")

    st.markdown("---")

    # --- Info Format CSV ---
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

# ──────────────────────────────────────────────────────────────────────
# Threshold dict
# ──────────────────────────────────────────────────────────────────────
thresholds = {
    "temp": {"warning": temp_warn, "danger": temp_danger},
    "vib":  {"warning": vib_warn,  "danger": vib_danger},
    "pres": {"warning": pres_warn, "danger": pres_danger},
}

# ──────────────────────────────────────────────────────────────────────
# Model check
# ──────────────────────────────────────────────────────────────────────
if not model_loaded:
    st.error(f"❌ Gagal memuat model: `{model_error}`")
    st.info("Pastikan file `xgboost_chain_model_24h.joblib` berada di direktori yang sama dengan `dashboard.py`.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────
# Main Content
# ──────────────────────────────────────────────────────────────────────
if uploaded_file is not None:
    # ── Baca & Validasi CSV ───────────────────────────────────────
    try:
        df_input = pd.read_csv(uploaded_file)
        filename = uploaded_file.name
        datetime_format = filename.split("_")[:5]
        date_string = "_".join(datetime_format)
        last_time = pd.to_datetime(date_string, format="%Y_%m_%d_%H_%M")
    except Exception as e:
        st.error(f"❌ Gagal membaca file CSV: {e}")
        st.stop()

    # df_mapped = auto_detect_columns(df_input)
    # if df_mapped is None:
    #     st.error("❌ Kolom CSV tidak sesuai format yang diharapkan.")
    #     st.markdown("**Kolom ditemukan:** `" + "`, `".join(df_input.columns.tolist()) + "`")
    #     st.markdown("**Kolom diharapkan:** `" + "`, `".join(EXPECTED_COLUMNS) + "`")
    #     st.info("Silakan sesuaikan nama kolom atau download template dari sidebar.")
    #     st.stop()

    # df_clean, warn_msg = validate_csv(df_input)
    # if warn_msg:
    #     st.warning(f"⚠️ {warn_msg}")

    df_features = df_input[FEATURES]
    n_rows = len(df_input)

    if n_rows == 0:
        st.error("❌ Tidak ada data valid untuk diprediksi setelah membersihkan NaN.")
        st.stop()

    # ── Preview Data ──────────────────────────────────────────────
    render_section_header("📂 Preview Data Input")

    render_kpi_row([
        {"icon": "📄", "label": "Total Baris", "value": str(n_rows), "unit": "data input valid"},
        # {"icon": "🔢", "label": "Total Kolom", "value": str(len(EXPECTED_COLUMNS)), "unit": "fitur lag terdeteksi"},
        {"icon": "📊", "label": "Total Prediksi", "value": str(n_rows * 24 * 3), "unit": f"{n_rows} × 24 step × 3 fitur"},
    ])

    with st.expander("👁️ Lihat Data Input", expanded=False):
        st.dataframe(df_features, use_container_width=True, height=300)

    st.markdown("---")

    # ── Jalankan Prediksi ─────────────────────────────────────────
    with st.spinner(f"🔄 Menjalankan prediksi untuk {n_rows} data..."):
        try:
            all_results = run_prediction(model, last_time, df_features.values, TARGETS, HORIZON)
        except Exception as e:
            st.error(f"❌ Error saat prediksi: {e}")
            st.stop()

    # Simpan input data ke results
    for i, r in enumerate(all_results):
        r["input"] = df_features.iloc[i].to_dict()

    # Hitung risk status
    all_results = compute_risk_for_results(all_results, thresholds)

    render_alert("success", f"✅ <strong>Prediksi berhasil!</strong> {n_rows} baris data telah diprediksi untuk 24 step ke depan.")

    # ── Ringkasan Batch ───────────────────────────────────────────
    render_section_header("📊 Ringkasan Seluruh Prediksi")

    n_danger = sum(1 for r in all_results if r["risk_status"] == "danger")
    n_warning = sum(1 for r in all_results if r["risk_status"] == "warning")
    n_safe = sum(1 for r in all_results if r["risk_status"] == "safe")
    pct_safe = (n_safe / n_rows) * 100 if n_rows > 0 else 0

    # Risk KPIs
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🟢 Aman</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{n_safe}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🟡 Waspada</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{n_warning}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔴 Bahaya</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{n_danger}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">✅ Tingkat Aman</div>
            <div class="kpi-value">{pct_safe:.1f}%</div>
            <div class="kpi-unit">data dalam batas aman</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Donut + Bar Chart ─────────────────────────────────────────
    render_section_header("📈 Visualisasi Risiko & Nilai Maksimum")

    col_donut, col_bar = st.columns([2, 5])

    with col_donut:
        fig_donut = create_risk_donut_chart(n_safe, n_warning, n_danger)
        st.plotly_chart(fig_donut, use_container_width=True, key="risk_donut", theme=None)

    with col_bar:
        st.caption("Garis putus-putus kuning = warning, merah = danger")
        fig_batch = create_batch_overview_chart(all_results, thresholds)
        st.plotly_chart(fig_batch, use_container_width=True, key="batch_overview", theme=None)

    st.markdown("---")

    # ── Tabel Ringkasan ───────────────────────────────────────────
    render_section_header("📋 Tabel Ringkasan Semua Data")
    print(f"all_results: {all_results}")
    df_summary = create_summary_dataframe(all_results)
    st.dataframe(df_summary, use_container_width=True, height=400)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # DETAIL PER DATA — Tabs
    # ══════════════════════════════════════════════════════════════
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
    steps = list(range(1, 25))

    tab_overview, tab_charts, tab_table = st.tabs(["📊 Ringkasan", "📈 Grafik Detail", "📋 Tabel"])

    # ── Tab: Ringkasan ────────────────────────────────────────────
    with tab_overview:
        render_input_summary(r["input"])
        st.markdown("---")
        render_prediction_stats(
            r["avg_temp"], r["max_temp"],
            r["avg_vib"], r["max_vib"],
            r["avg_pres"], r["max_pres"],
            r["risk_status"],
        )
        st.markdown("---")
        render_risk_alerts(r["max_temp"], r["max_vib"], r["max_pres"], thresholds)

    # ── Tab: Grafik Detail ────────────────────────────────────────
    with tab_charts:
        st.markdown(f"#### 📈 Grafik Prediksi 24-Step — Data ke-{selected_row}")
        fig_detail = create_forecast_chart(steps, r["temp_pred"], r["vib_pred"], r["pres_pred"])
        st.plotly_chart(fig_detail, use_container_width=True, key="detail_forecast", theme=None)

        st.markdown("---")

        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.markdown("#### 🔀 Overlay Semua Fitur")
            fig_comb = create_combined_chart(steps, r["temp_pred"], r["vib_pred"], r["pres_pred"])
            st.plotly_chart(fig_comb, use_container_width=True, key="detail_combined", theme=None)

        with c_right:
            st.markdown("#### 🗺️ Korelasi Antar Fitur")
            df_corr = pd.DataFrame({
                "temperature": r["temp_pred"],
                "vibration": r["vib_pred"],
                "pressure_bar": r["pres_pred"],
            })
            fig_hm = create_heatmap_chart(df_corr)
            st.plotly_chart(fig_hm, use_container_width=True, key="detail_heatmap", theme=None)

    # ── Tab: Tabel ────────────────────────────────────────────────
    with tab_table:
        st.markdown(f"#### 📋 Tabel Detail Prediksi — Data ke-{selected_row}")

        df_detail = pd.DataFrame({
            "Step": steps,
            "Temperature (°C)": r["temp_pred"],
            "Vibration (mm/s)": r["vib_pred"],
            "Pressure (bar)": r["pres_pred"],
        }).set_index("Step")

        st.dataframe(
            df_detail.style.format({
                "Temperature (°C)": "{:.4f}",
                "Vibration (mm/s)": "{:.6f}",
                "Pressure (bar)": "{:.4f}",
            }).background_gradient(
                cmap="YlOrRd", subset=["Temperature (°C)"]
            ).background_gradient(
                cmap="Purples", subset=["Vibration (mm/s)"]
            ).background_gradient(
                cmap="Blues", subset=["Pressure (bar)"]
            ),
            use_container_width=True,
            height=500,
        )

    st.markdown("---")

    # ── Download Hasil ────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────
st.markdown("---")
render_footer()
