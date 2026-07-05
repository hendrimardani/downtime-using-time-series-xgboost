import streamlit as st

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

def render_kpi_card(label, value, unit="", icon=""):
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
            render_kpi_card(
                label=card["label"],
                value=card["value"],
                unit=card.get("unit", ""),
                icon=card.get("icon", ""),
            )

def render_status_badge(status):
    """Return an HTML string for a coloured status badge.
    Parameters
    ----------
    status : str
        One of 'safe', 'warning', 'danger'.
    Returns
    -------
    str
        HTML snippet with the appropriate CSS class and emoji.
    """
    mapping = {
        "safe": ("status-safe", "🟢 AMAN"),
        "warning": ("status-warning", "🟡 WASPADA"),
        "danger": ("status-danger", "🔴 BAHAYA"),
    }
    css_class, text = mapping.get(status, ("status-safe", "🟢 AMAN"))
    return f'<span class="{css_class}">{text}</span>'

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

def render_section_header(text):
    """Render a styled section header."""
    st.markdown(
        f'<div class="section-header">{text}</div>',
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
                        <tr><td style="padding:6px 8px;">Input</td><td style="padding:6px 8px;">6 features</td></tr>
                        <tr><td style="padding:6px 8px;">Output</td><td style="padding:6px 8px;">24-step × 3 features</td></tr>
                        <tr><td style="padding:6px 8px;">Total</td><td style="padding:6px 8px;">72 values per row</td></tr>
                        <tr><td style="padding:6px 8px;">Mode</td><td style="padding:6px 8px;">Batch</td></tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
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