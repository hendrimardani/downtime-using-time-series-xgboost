import pandas as pd
import streamlit as st
import os
import streamlit.components.v1 as components
from utils.data import export_logging_df
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

def render_header():
    """Render the main dashboard header with title and subtitle."""
    st.markdown(
        """
        <div class="dashboard-header">
            <h1 class="dashboard-title">⚙️ Prediksi Downtime Mesin</h1>
            <p class="dashboard-subtitle">
                Dashboard prediksi 24-step horizon menggunakan XGBoost RegressorChain
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _render_kpi_card(label, value, unit="", icon=""):
    """Render a single KPI metric card.
    Parameters
    ----------
    label : str
        Metric label text.
    value : str | int | float
        Metric value to display.
    unit : str, optional
        Unit suffix shown after the value.
    icon : str, optional
        Emoji / icon placed before the label.
    """
    icon_html = f"{icon} " if icon else ""
    unit_html = f'<div class="kpi-unit">{unit}</div>' if unit else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{icon_html}{label}</div>
            <div class="kpi-value">{value}</div>
            {unit_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_kpi_row(cards_data):
    """Render a row of KPI cards inside equal-width columns.

    Parameters
    ----------
    cards_data : list[dict]
        Each dict must contain keys: label, value.
        Optional keys: unit, icon.
    """
    cols = st.columns(len(cards_data))
    for col, card in zip(cols, cards_data):
        with col:
            _render_kpi_card(
                label=card["label"],
                value=card["value"],
                unit=card.get("unit", ""),
                icon=card.get("icon", ""),
            )

def render_alert(alert_type, message):
    """Render a styled alert box.

    Parameters
    ----------
    alert_type : str
        One of 'danger', 'warning', 'success'.
    message : str
        Alert body text / HTML.
    """
    st.markdown(
        f"""
        <div class="alert-box alert-{alert_type}">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_welcome_page():
    """Render the welcome page shown before a CSV file is uploaded."""
    st.markdown(
        """
        <div style="text-align:center; padding:2.5rem 1rem 1rem;">
            <div style="font-size:5rem;">🏭</div>
            <h2 style="color:#E0E0E0; margin-top:0.5rem;">
                Selamat Datang di Dashboard Prediksi Downtime Mesin
            </h2>
            <p style="color:#9E9E9E; font-size:1.05rem; max-width:680px; margin:auto;">
                Dashboard ini memprediksi <b>suhu</b>, <b>getaran</b>, dan
                <b>tekanan</b> untuk <b>24 langkah ke depan</b> menggunakan
                model <b>XGBoost RegressorChain</b>.
            </p>
            <p style="color:#BDBDBD; margin-top:1.2rem; font-size:1rem;">
                📂 Silakan <b>upload file CSV</b> melalui sidebar untuk memulai prediksi.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="background:rgba(255,255,255,0.04); backdrop-filter:blur(12px);
                    border:1px solid rgba(255,255,255,0.08); border-radius:16px;
                    padding:1.5rem; margin-top:1rem;">
            <h4 style="color:#E0E0E0; margin-top:0;">✨ Fitur yang Tersedia</h4>
            <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                <thead>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.15);">
                        <th style="text-align:left; padding:8px; color:#90CAF9;">Nama</th>
                        <th style="text-align:left; padding:8px; color:#90CAF9;">Deskripsi</th>
                    </tr>
                </thead>
                <tbody style="color:#BDBDBD;">
                    <tr><td style="padding:6px 8px;">Auto Refresh</td><td style="padding:6px 8px;">Auto refresh secara realtime (1 menit, 1 jam, dan 1 hari) disesuaikan sesuai kebutuhan.</td></tr>
                    <tr><td style="padding:6px 8px;">Export Hasil Prediksi</td><td style="padding:6px 8px;">Ekspor hasil prediksi ke berbagai format seperti CSV dan JSON untuk analisis lebih lanjut.</td></tr>
                    <tr><td style="padding:6px 8px;">Deteksi Status Risiko Downtime</td><td style="padding:6px 8px;">Mengklasifikasikan tiap prediksi ke dalam status Aman, Waspada, dan Bahaya secara otomatis (early sistem warning)</td></tr>
                    <tr><td style="padding:6px 8px;">Tabel Prediksi</td><td style="padding:6px 8px;">Tabel detail dengan pewarnaan status per baris prediksi</td></tr>
                    <tr><td style="padding:6px 8px;">Countdown Timer</td><td style="padding:6px 8px;">Menampilkan waktu mundur dan progress bar hingga refresh berikutnya</td></tr>
                    <tr><td style="padding:6px 8px;">Ringkasan Batch</td><td style="padding:6px 8px;">Menampilkan jumlah dan persentase data yang berstatus Aman, Waspada, dan Bahaya</td></tr>
                    <tr><td style="padding:6px 8px;">Logging Tracking</td><td style="padding:6px 8px;">Menampilkan informasi logging eksekusi autorefresh dan script di background</td></tr>
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(
            """
            <div style="background:rgba(255,255,255,0.04); backdrop-filter:blur(12px);
                        border:1px solid rgba(255,255,255,0.08); border-radius:16px;
                        padding:1.5rem; margin-top:1rem;">
                <h4 style="color:#E0E0E0; margin-top:0;">📋 Format CSV yang Diharapkan</h4>
                <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.15);">
                            <th style="text-align:left; padding:8px; color:#90CAF9;">No</th>
                            <th style="text-align:left; padding:8px; color:#90CAF9;">Kolom</th>
                        </tr>
                    </thead>
                    <tbody style="color:#BDBDBD;">
                        <tr><td style="padding:6px 8px;">1</td><td style="padding:6px 8px;">temperature_C_lag_1</td></tr>
                        <tr><td style="padding:6px 8px;">2</td><td style="padding:6px 8px;">temperature_C_lag_24</td></tr>
                        <tr><td style="padding:6px 8px;">3</td><td style="padding:6px 8px;">vibration_mm_s_lag_1</td></tr>
                        <tr><td style="padding:6px 8px;">4</td><td style="padding:6px 8px;">vibration_mm_s_lag_24</td></tr>
                        <tr><td style="padding:6px 8px;">5</td><td style="padding:6px 8px;">pressure_bar_lag_1</td></tr>
                        <tr><td style="padding:6px 8px;">6</td><td style="padding:6px 8px;">pressure_bar_lag_24</td></tr>
                        <tr><td style="padding:6px 8px;">7</td><td style="padding:6px 8px;">day_of_week</td></tr>
                        <tr><td style="padding:6px 8px;">8</td><td style="padding:6px 8px;">is_holiday</td></tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
            <div style="background:rgba(255,255,255,0.04); backdrop-filter:blur(12px);
                        border:1px solid rgba(255,255,255,0.08); border-radius:16px;
                        padding:1.5rem; margin-top:1rem;">
                <h4 style="color:#E0E0E0; margin-top:0;">🤖 Informasi Model</h4>
                <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.15);">
                            <th style="text-align:left; padding:8px; color:#90CAF9;">Parameter</th>
                            <th style="text-align:left; padding:8px; color:#90CAF9;">Nilai</th>
                        </tr>
                    </thead>
                    <tbody style="color:#BDBDBD;">
                        <tr><td style="padding:6px 8px;">Algorithm</td><td style="padding:6px 8px;">XGBoost + RegressorChain</td></tr>
                        <tr><td style="padding:6px 8px;">Input</td><td style="padding:6px 8px;">8 features</td></tr>
                        <tr><td style="padding:6px 8px;">Output</td><td style="padding:6px 8px;">24-step × 3 features</td></tr>
                        <tr><td style="padding:6px 8px;">Total</td><td style="padding:6px 8px;">72 values per row</td></tr>
                        <tr><td style="padding:6px 8px;">Mode</td><td style="padding:6px 8px;">Batch</td></tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_autorefresh(header, output_logging):
    status = None

    st.markdown(header)
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
        try:
            refresh_count = st_autorefresh(
                interval=refresh_interval_ms,
                key="auto_refresh_counter",
            )

            refresh_interval_sec = refresh_interval_ms // 1000
            last_refresh_time = datetime.now().strftime('%H:%M:%S')
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
            status = "berhasil"
        except Exception as e:
            print(f"Error logging auto refresh: ", e)
            status = "gagal"

        export_logging_df(output_logging, status)

    else:
        st.info("💤 Auto refresh **nonaktif**")

    st.markdown("---")

def render_upload_data(header):
    st.markdown(header)
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
    st.markdown("## 📝 Input Data")
    
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
    return uploaded_file

def render_section_header(text):
    """Render a styled section header."""
    st.markdown(
        f'<div class="section-header">{text}</div>',
        unsafe_allow_html=True,
    )

def render_task_scheduler_tutorial(header):
    """Render tutorial Windows Task Scheduler di sidebar menggunakan st.expander.

    Menampilkan panduan langkah-langkah untuk menjadwalkan script Python
    agar berjalan otomatis menggunakan Windows Task Scheduler, dilengkapi
    gambar ilustrasi di setiap langkah.
    """
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _IMG_DIR = os.path.join(_BASE_DIR, "assets", "tutorial")

    st.markdown("---")
    st.markdown(header)

    with st.expander("🖥️ Tutorial Windows Task Scheduler", expanded=False):

        # ── Prasyarat ─────────────────────────────────────────
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <p style="color:#90CAF9; font-weight:600; margin-bottom:6px;">
                📌 Prasyarat
            </p>
            <ul style="margin-top:0; padding-left:1.2rem;">
                <li>Python sudah terinstall terutama lauchernya <code>.exe</code></li>
                <li>Mengetahui lokasi file script <code>.py</code> yang ingin dijadwalkan</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Langkah 1 ────────────────────────────────────────
        st.markdown(
            """
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.1); margin:12px 0;">
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <p style="color:#90CAF9; font-weight:600;">
                Langkah 1 — Buka Task Scheduler
            </p>
            <ol style="margin-top:4px; padding-left:1.2rem;">
                <li>Tekan <kbd style="background:#333; padding:2px 6px; border-radius:4px; font-size:0.82rem;">Win + R</kbd></li>
                <li>Ketik <code>taskschd.msc</code> lalu tekan <b>Enter</b></li>
            </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step1_run_dialog.png"),
            caption="Dialog Run — ketik taskschd.msc",
            use_container_width=True,
        )

        # ── Langkah 2 ────────────────────────────────────────
        st.markdown(
            """
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.1); margin:12px 0;">
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <p style="color:#90CAF9; font-weight:600;">
                Langkah 2 — Buat Task Baru
            </p>
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Klik <b>Create Task…</b> di panel kanan</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step2_create_task.png"),
            caption="Pilih Create Task...",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Pada atribut <b>Name:</b> isi nama script yang akan dijalankan misalnya dalam kasus ini dinamai dengan <b>Autome Run Downtime</b> untuk atribut <b>Description:</b> optional</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step2_create_name_task.png"),
            caption="General - Isi Atribut Name dan Description (Optional)",
            use_container_width=True,
        )

        # ── Langkah 3 ────────────────────────────────────────
        st.markdown(
            """
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.1); margin:12px 0;">
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <p style="color:#90CAF9; font-weight:600;">
                Langkah 3 — Atur Jadwal (Trigger)
            </p>
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Pindah ke tab <b>Triggers</b> kemudian pilih <b>New</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step3_click_new_trigger.png"),
            caption="Trigger — Pilih New",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Pilih <b>Daily</b> karena disini akan dilakukan automasi harian, lalu centang <b>Repeat task every</b> isi setiap berapa menit/jam sekali <i>script</i> dijalankan, dalam kasus ini akan dilakukan automasi setiap 1 hari sekali. Tekan <b>Ok</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step3_new_trigger.png"),
            caption="Trigger — Pilih Penjadwalan Skrip (Harian, Mingguan atau Bulanan)",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Maka trigger yang baru saja dibuat akan terdaftar di kolom yang tadinya kosong.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step3_registered_trigger.png"),
            caption="Trigger — Trigger Terdaftar",
            use_container_width=True,
        )

        # ── Langkah 4 ────────────────────────────────────────
        st.markdown(
            """
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.1); margin:12px 0;">
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <p style="color:#90CAF9; font-weight:600;">
                Langkah 4 — Atur Aksi (Action) 
            </p>
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Pindah ke tab <b>Triggers</b> kemudian pilih <b>New</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step4_new_action.png"),
            caption="Action — Pilih New",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Isi beberapa atribut yang wajib diisi seperti <b>Program/script</b>, <b>Add arguments (optional)</b>, <b>Start in</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step4_atribut_action.png"),
            caption="Action — Isi Beberapa Atribut",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Cari lokasi launcher python yang sudah diinstal, dalam kasus ini lokasi python berada di <code>C:"\\Users"\\hendr\AppData"\\Local"\\Programs"\\Python"\\Python312"\\python.exe</code> <b>tanpa tanda kutip 2 (")</b> lalu salin lokasi tersebut di atribut <b>Progam/script</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step4_python_exe_location.png"),
            caption="Action — Cari Lokasi Python Launcher (exe)",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Untuk atribut <b>Add arguments (optional)</b> isi dengan <i>script</i> python yang akan dijalankan dalam hal ini file <b>preprocessing.py</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step4_fill_add_arguments.png"),
            caption="Action — File Eksekusi Script Python di Background",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Untuk atribut <b>Start in (optional)</b> isi dengan lokasi folder dimana letak script itu berada (tanpa menyebutkan script yang akan dieksekusi). Misalnya dalam kasus ini <i>script</i> <b>preprocessing.py</b> berada di <code>C:"\\Users"\\hendr"\\Downloads"\\Tugas Akhir Timeseries Streamlit"\\utils</code><b>tanpa tanda kutip 2 (")</b>, maka tidak perlu mencantumkan nama <b>preprocessing.py</b> karena tugas tersebut bagian atribut <b>Add arguments (optional)</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step4_fill_start_in.png"),
            caption="Action — File Eksekusi Script Python di Background",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Jika sudah terisi semua tekan <b>Ok</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step4_action_ok.png"),
            caption="Action — Atribut Sudah Terisi",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Maka akan kembali ke tampilan <b>Create Task</b> tekan lagi <b>Ok</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step4_create_task_ok.png"),
            caption="Action — Create Task Ok",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Maka akan kembali ke tampilan awal<b>Task Scheduler</b> terlihat bahwa task yang baru saja kita buat sudah terdaftar di <b>Task Scheduler</b></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step4_task_scheduler_ok.png"),
            caption="Action — Task Scheduler Ok",
            use_container_width=True,
        )

        # ── Langkah 5 ────────────────────────────────────────
        st.markdown(
            """
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.1); margin:12px 0;">
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <p style="color:#90CAF9; font-weight:600;">
                Langkah 5 — Selesai &amp; Uji Coba
            </p>
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Terakhir jalankan tugas tersebut dengan cara pilih ke tugas yang baru saja kita buat, lalu tekan <b>Run</b> agar menjalankan <i>script</i> python di background sesuai dengan iterasi yang kita pilih di awal (1 menit, 1 jam, atau 1 hari).</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step5_test_scheduler.png"),
            caption="Uji coba — Task Scheduler",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Maka akan muncul <b>Command Prompt (CMD)</b> jangan khawatir hal tersebut normal itu berarti <i>script</i> python yang berjalan di background sudah berfungsi dengan baik.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step5_cmd.png"),
            caption="Uji coba — Tampil Command Prompt",
            use_container_width=True,
        )
        st.markdown(
            """
            <div style="font-size:0.88rem; color:#BDBDBD; line-height:1.7;">
            <ul style="margin-top:4px; padding-left:1.2rem;">
                <li>Terakhir, tunggu beberapa menit maka akan muncul berkas baru bernama <b>preprocessed_dataset.csv</b>. Dataset tersebut berasal dari hasil preprocessing yang dijalankan <i>script</i> di background, dataset inilah nantinya yang akan digunakan sebagai input data downtime.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image(
            os.path.join(_IMG_DIR, "step5_preprocessed_dataset_created.png"),
            caption="Uji coba — Preprocessed Dataset Terbuat Secara Otomatis",
            use_container_width=True,
        )

def render_kpi_statistics(status, header, value, value2=None):
    if status == "normal":
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{header}</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
        </div>
        """, unsafe_allow_html=True)
    elif status == "waspada":
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{header}</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">[{value} - {value2}]</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{header}</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
        </div>
        """, unsafe_allow_html=True)

def render_kpi_summary(status, header, value, n_rows):
    if status == "normal":
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{header}</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)
    elif status == "waspada":
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{header}</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{header}</div>
            <div class="kpi-value" style="background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
            <div class="kpi-unit">dari {n_rows} data</div>
        </div>
        """, unsafe_allow_html=True)

def render_download_button(df, type, output_path):
    if type.lower() == "csv":
        st.download_button(
            label="📥 Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=output_path,
            mime="text/csv",
            use_container_width=True,
        )
    elif type.lower() == "json":
        st.download_button(
            label="📥 Download JSON",
            data=df.to_json(orient="records", indent=2).encode("utf-8"),
            file_name=output_path,
            mime="application/json",
            use_container_width=True,
        )

def render_footer():
    """Render the dashboard footer."""
    st.markdown(
        """
        <div style="text-align:center; padding:2rem 0 1rem; color:#757575;
                    font-size:0.85rem; border-top:1px solid rgba(255,255,255,0.06);
                    margin-top:3rem;">
            ⚙️ Prediksi Downtime Mesin - XGBoost RegressionChain
        </div>
        """,
        unsafe_allow_html=True,
    )