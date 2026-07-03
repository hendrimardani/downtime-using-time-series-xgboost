"""
Reusable Streamlit UI component functions.
All rendering uses st.markdown with unsafe_allow_html for custom HTML/CSS styling.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# 1. Header
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 2. Single KPI Card
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 3. KPI Row (multiple cards in columns)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 4. Status Badge
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 5. Alert Box
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 6. Section Header
# ---------------------------------------------------------------------------
def render_section_header(text):
    """Render a styled section header."""
    st.markdown(
        f'<div class="section-header">{text}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 7. Welcome / Landing Page
# ---------------------------------------------------------------------------
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
                        <tr><td style="padding:6px 8px;">1</td><td style="padding:6px 8px;">temperature_lag1</td></tr>
                        <tr><td style="padding:6px 8px;">2</td><td style="padding:6px 8px;">temperature_lag24</td></tr>
                        <tr><td style="padding:6px 8px;">3</td><td style="padding:6px 8px;">vibration_lag1</td></tr>
                        <tr><td style="padding:6px 8px;">4</td><td style="padding:6px 8px;">vibration_lag24</td></tr>
                        <tr><td style="padding:6px 8px;">5</td><td style="padding:6px 8px;">pressure_bar_lag1</td></tr>
                        <tr><td style="padding:6px 8px;">6</td><td style="padding:6px 8px;">pressure_bar_lag24</td></tr>
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


# ---------------------------------------------------------------------------
# 8. Footer
# ---------------------------------------------------------------------------
def render_footer():
    """Render the dashboard footer."""
    st.markdown(
        """
        <div style="text-align:center; padding:2rem 0 1rem; color:#757575;
                    font-size:0.85rem; border-top:1px solid rgba(255,255,255,0.06);
                    margin-top:3rem;">
            ⚙️ Prediksi Downtime Mesin — Tugas Akhir | Powered by XGBoost RegressorChain &amp; Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 9. Risk Alerts
# ---------------------------------------------------------------------------
def render_risk_alerts(max_temp, max_vib, max_pres, thresholds):
    """Evaluate max predicted values against thresholds and render alerts.

    Parameters
    ----------
    max_temp : float
        Maximum predicted temperature value.
    max_vib : float
        Maximum predicted vibration value.
    max_pres : float
        Maximum predicted pressure value.
    thresholds : dict
        Format::

            {
                'temp': {'warning': float, 'danger': float},
                'vib':  {'warning': float, 'danger': float},
                'pres': {'warning': float, 'danger': float},
            }
    """
    alerts_fired = False

    # --- Temperature ---
    if max_temp >= thresholds["temp"]["danger"]:
        render_alert("danger", f"🔴 <b>Suhu BAHAYA!</b> Maks prediksi: <b>{max_temp:.2f}</b> (batas: {thresholds['temp']['danger']})")
        alerts_fired = True
    elif max_temp >= thresholds["temp"]["warning"]:
        render_alert("warning", f"🟡 <b>Suhu WASPADA!</b> Maks prediksi: <b>{max_temp:.2f}</b> (batas: {thresholds['temp']['warning']})")
        alerts_fired = True

    # --- Vibration ---
    if max_vib >= thresholds["vib"]["danger"]:
        render_alert("danger", f"🔴 <b>Getaran BAHAYA!</b> Maks prediksi: <b>{max_vib:.2f}</b> (batas: {thresholds['vib']['danger']})")
        alerts_fired = True
    elif max_vib >= thresholds["vib"]["warning"]:
        render_alert("warning", f"🟡 <b>Getaran WASPADA!</b> Maks prediksi: <b>{max_vib:.2f}</b> (batas: {thresholds['vib']['warning']})")
        alerts_fired = True

    # --- Pressure ---
    if max_pres >= thresholds["pres"]["danger"]:
        render_alert("danger", f"🔴 <b>Tekanan BAHAYA!</b> Maks prediksi: <b>{max_pres:.2f}</b> (batas: {thresholds['pres']['danger']})")
        alerts_fired = True
    elif max_pres >= thresholds["pres"]["warning"]:
        render_alert("warning", f"🟡 <b>Tekanan WASPADA!</b> Maks prediksi: <b>{max_pres:.2f}</b> (batas: {thresholds['pres']['warning']})")
        alerts_fired = True

    if not alerts_fired:
        render_alert("success", "🟢 <b>Semua parameter dalam batas AMAN.</b> Tidak ada risiko downtime terdeteksi.")


# ---------------------------------------------------------------------------
# 10. Input Summary
# ---------------------------------------------------------------------------
def render_input_summary(input_data):
    """Render 3-column KPI cards summarising the uploaded input row.

    Parameters
    ----------
    input_data : dict
        Keys: temperature_C_lag_1, temperature_C_lag_24, vibration_mm_s_lag_1,
              vibration_mm_s_lag_24, pressure_bar_lag_1, pressure_bar_lag_24.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        render_kpi_card("Temperature Lag-1", f"{input_data['temperature_C_lag_1']:.2f}", unit="°C", icon="🌡️")
        render_kpi_card("Temperature Lag-24", f"{input_data['temperature_C_lag_24']:.2f}", unit="°C", icon="🌡️")

    with col2:
        render_kpi_card("Vibration Lag-1", f"{input_data['vibration_mm_s_lag_1']:.2f}", unit="mm/s", icon="📳")
        render_kpi_card("Vibration Lag-24", f"{input_data['vibration_mm_s_lag_24']:.2f}", unit="mm/s", icon="📳")

    with col3:
        render_kpi_card("Pressure Lag-1", f"{input_data['pressure_bar_lag_1']:.2f}", unit="bar", icon="🔧")
        render_kpi_card("Pressure Lag-24", f"{input_data['pressure_bar_lag_24']:.2f}", unit="bar", icon="🔧")


# ---------------------------------------------------------------------------
# 11. Prediction Statistics
# ---------------------------------------------------------------------------
def render_prediction_stats(avg_temp, max_temp, avg_vib, max_vib, avg_pres, max_pres, risk_status):
    """Render 4-column KPI cards for prediction statistics.

    Parameters
    ----------
    avg_temp, max_temp : float
        Average and max predicted temperature.
    avg_vib, max_vib : float
        Average and max predicted vibration.
    avg_pres, max_pres : float
        Average and max predicted pressure.
    risk_status : str
        Overall risk status: 'safe', 'warning', or 'danger'.
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_card("Avg Suhu", f"{avg_temp:.2f}", unit="°C", icon="🌡️")
        render_kpi_card("Max Suhu", f"{max_temp:.2f}", unit="°C", icon="🔥")

    with col2:
        render_kpi_card("Avg Getaran", f"{avg_vib:.2f}", unit="mm/s", icon="📳")
        render_kpi_card("Max Getaran", f"{max_vib:.2f}", unit="mm/s", icon="⚡")

    with col3:
        render_kpi_card("Avg Tekanan", f"{avg_pres:.2f}", unit="bar", icon="🔧")
        render_kpi_card("Max Tekanan", f"{max_pres:.2f}", unit="bar", icon="💥")

    with col4:
        badge_html = render_status_badge(risk_status)
        st.markdown(
            f"""
            <div class="kpi-card" style="text-align:center;">
                <div class="kpi-label">🛡️ Status Risiko</div>
                <div class="kpi-value" style="margin-top:0.75rem;">{badge_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
