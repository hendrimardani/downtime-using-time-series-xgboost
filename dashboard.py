import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
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
    # ── Auto Refresh ──────────────────────────────────────────────
    st.markdown("## 🔄 Auto Refresh")

    refresh_options = {
        "Nonaktif": None,
        "⏱️ Setiap 1 Menit": 60 * 1000,
        "🕐 Setiap 1 Jam": 60 * 60 * 1000,
        "📅 Setiap 1 Hari": 24 * 60 * 60 * 1000,
    }

    selected_refresh = st.selectbox(
        "Interval Refresh",
        options=list(refresh_options.keys()),
        index=0,
        help="Pilih interval auto refresh halaman dashboard",
    )

    refresh_interval_ms = refresh_options[selected_refresh]

    if refresh_interval_ms is not None:
        refresh_count = st_autorefresh(
            interval=refresh_interval_ms,
            key="auto_refresh_counter",
        )

        refresh_interval_sec = refresh_interval_ms // 1000
        last_refresh_time = datetime.now().strftime('%H:%M:%S')

        import streamlit.components.v1 as components

        countdown_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            .countdown-container {{
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                padding: 1rem;
            }}
            .countdown-header {{
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 8px;
            }}
            .countdown-header .icon {{ font-size: 1.3rem; }}
            .countdown-header .label {{
                color: #E0E0E0;
                font-weight: 600;
                font-size: 0.95rem;
            }}
            .countdown-time {{
                font-size: 1.8rem;
                font-weight: 700;
                text-align: center;
                padding: 0.3rem 0;
                font-family: 'Courier New', monospace;
                background: linear-gradient(135deg, #60a5fa, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .progress-track {{
                background: rgba(255,255,255,0.08);
                border-radius: 8px;
                height: 8px;
                margin: 8px 0;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                border-radius: 8px;
                background: linear-gradient(90deg, #60a5fa, #a78bfa);
                width: 100%;
                transition: width 1s linear;
            }}
            .countdown-footer {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 6px;
            }}
            .countdown-footer span {{
                color: #9E9E9E;
                font-size: 0.78rem;
            }}
            .countdown-footer strong {{ color: #BDBDBD; }}
            .countdown-footer code {{
                color: #BDBDBD;
                background: none;
                font-family: 'Courier New', monospace;
            }}
        </style>
        </head>
        <body>
            <div class="countdown-container">
                <div class="countdown-header">
                    <span class="icon">⏳</span>
                    <span class="label">Refresh berikutnya dalam</span>
                </div>
                <div class="countdown-time" id="countdown-time">00:00:00</div>
                <div class="progress-track">
                    <div class="progress-fill" id="countdown-bar"></div>
                </div>
                <div class="countdown-footer">
                    <span>🔁 Refresh ke-<strong>{refresh_count}</strong></span>
                    <span>🕑 <code>{last_refresh_time}</code></span>
                </div>
            </div>

            <script>
            (function() {{
                const totalSeconds = {refresh_interval_sec};
                const startTime = Date.now();

                function pad(n) {{ return String(n).padStart(2, '0'); }}

                function update() {{
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    let remaining = totalSeconds - elapsed;
                    if (remaining < 0) remaining = 0;

                    const h = Math.floor(remaining / 3600);
                    const m = Math.floor((remaining % 3600) / 60);
                    const s = remaining % 60;

                    document.getElementById('countdown-time').textContent =
                        pad(h) + ':' + pad(m) + ':' + pad(s);
                    document.getElementById('countdown-bar').style.width =
                        ((remaining / totalSeconds) * 100) + '%';

                    if (remaining > 0) {{
                        setTimeout(update, 1000);
                    }}
                }}
                update();
            }})();
            </script>
        </body>
        </html>
        """
        components.html(countdown_html, height=150)
    else:
        st.info("💤 Auto refresh **nonaktif**")

    st.markdown("---")

    # ── Upload Data ──────────────────────────────────────────────
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
        df_input["timestamp"] = pd.to_datetime(df_input["timestamp"], format="mixed")
        last_time = df_input["timestamp"].iloc[0]
        # last_time = pd.to_datetime(date_string, format="mixed")
        print("last_time", last_time)
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
        # df_datetime = df_features.copy()
        # df_datetime["timestamp"] = last_time
        # new_sort_features = [
        #     "timestamp", "temperature_C_lag_1", "temperature_C_lag_24",
        #     "vibration_mm_s_lag_1", "vibration_mm_s_lag_24",
        #     "pressure_bar_lag_1", "pressure_bar_lag_24",
        #     "day_of_week", "is_holiday"
        # ]
        # df_datetime = df_datetime[new_sort_features]
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
