import streamlit as st


def inject_css() -> None:
    """Inject premium dark-theme dashboard CSS into the Streamlit app."""
    st.markdown(
        """
        <style>
        /* ── Google Font ─────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── CSS Variables ───────────────────────────────────────── */
        :root {
            --font-main: 'Inter', sans-serif;
            --bg-primary: #0a0a14;
            --bg-secondary: #0f0f1a;
            --bg-card: rgba(22, 22, 40, 0.65);
            --bg-card-hover: rgba(30, 30, 55, 0.75);
            --border-subtle: rgba(99, 102, 241, 0.12);
            --border-hover: rgba(99, 102, 241, 0.30);
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --primary: #6366f1;
            --primary-light: #818cf8;
            --danger: #ef4444;
            --warning: #f59e0b;
            --success: #10b981;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-pill: 50px;
            --shadow-glow: 0 8px 32px rgba(99, 102, 241, 0.25);
            --transition-default: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* ── Base / Global ───────────────────────────────────────── */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: var(--font-main) !important;
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }

        [data-testid="stAppViewContainer"] > .main {
            background: linear-gradient(180deg, var(--bg-primary) 0%, #0d0d1f 100%);
        }

        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }

        /* ── Sidebar ─────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(195deg, #0f0f1a 0%, #1a1a2e 100%) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.5rem !important;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label {
            color: var(--text-secondary) !important;
            font-family: var(--font-main) !important;
        }

        /* ── Glassmorphism Card Base ─────────────────────────────── */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            transition: var(--transition-default);
        }

        .glass-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            transform: translateY(-3px);
            box-shadow: var(--shadow-glow);
        }

        /* ── KPI Cards ───────────────────────────────────────────── */
        .kpi-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.4rem 1.2rem;
            text-align: center;
            transition: var(--transition-default);
            position: relative;
            overflow: hidden;
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--primary-light));
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.20);
            border-color: var(--border-hover);
        }

        .kpi-card:hover::before {
            opacity: 1;
        }

        .kpi-label {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }

        .kpi-value {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary-light), #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
            margin-bottom: 0.25rem;
        }

        .kpi-unit {
            font-size: 0.75rem;
            color: var(--text-muted);
            font-weight: 400;
        }

        /* ── Status Badges ───────────────────────────────────────── */
        .status-safe {
            display: inline-block;
            padding: 0.3rem 1rem;
            border-radius: var(--radius-pill);
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08));
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #34d399;
        }

        .status-warning {
            display: inline-block;
            padding: 0.3rem 1rem;
            border-radius: var(--radius-pill);
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.08));
            border: 1px solid rgba(245, 158, 11, 0.35);
            color: #fbbf24;
        }

        .status-danger {
            display: inline-block;
            padding: 0.3rem 1rem;
            border-radius: var(--radius-pill);
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.08));
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #f87171;
        }

        /* ── Alert Boxes ─────────────────────────────────────────── */
        .alert-box {
            border-radius: var(--radius-md);
            padding: 1rem 1.25rem;
            margin: 0.75rem 0;
            font-size: 0.9rem;
            line-height: 1.6;
            font-family: var(--font-main);
        }

        .alert-danger {
            background: rgba(239, 68, 68, 0.08);
            border-left: 4px solid var(--danger);
            color: #fca5a5;
        }

        .alert-warning {
            background: rgba(245, 158, 11, 0.08);
            border-left: 4px solid var(--warning);
            color: #fcd34d;
        }

        .alert-success {
            background: rgba(16, 185, 129, 0.08);
            border-left: 4px solid var(--success);
            color: #6ee7b7;
        }

        /* ── Dashboard Header ────────────────────────────────────── */
        .dashboard-header {
            text-align: center;
            padding: 1rem 0 1.5rem 0;
        }

        .dashboard-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.35rem;
            line-height: 1.2;
        }

        .dashboard-subtitle {
            font-size: 1rem;
            color: var(--text-muted);
            font-weight: 400;
            letter-spacing: 0.3px;
        }

        /* ── Section Header ──────────────────────────────────────── */
        .section-header {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--text-primary);
            padding-bottom: 0.6rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid transparent;
            border-image: linear-gradient(90deg, var(--primary), var(--primary-light), transparent) 1;
            font-family: var(--font-main);
        }

        /* ── Upload Area ─────────────────────────────────────────── */
        .upload-info {
            border: 2px dashed var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 2rem;
            text-align: center;
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: var(--transition-default);
        }

        .upload-info:hover {
            border-color: var(--primary);
            background: var(--bg-card-hover);
        }

        /* ── Divider / hr ────────────────────────────────────────── */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent,
                var(--border-subtle),
                rgba(99, 102, 241, 0.25),
                var(--border-subtle),
                transparent
            );
            margin: 1.5rem 0;
        }

        /* ── Tabs ────────────────────────────────────────────────── */
        [data-testid="stTabs"] {
            background: transparent;
        }

        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 0;
            background: rgba(15, 15, 26, 0.6);
            border-radius: var(--radius-sm);
            padding: 4px;
            border: 1px solid var(--border-subtle);
        }

        [data-testid="stTabs"] [data-baseweb="tab"] {
            background: transparent !important;
            color: var(--text-muted) !important;
            border: none !important;
            border-radius: 6px;
            padding: 0.5rem 1.2rem;
            font-family: var(--font-main) !important;
            font-weight: 500;
            font-size: 0.88rem;
            transition: var(--transition-default);
        }

        [data-testid="stTabs"] [data-baseweb="tab"]:hover {
            color: var(--text-primary) !important;
            background: rgba(99, 102, 241, 0.08) !important;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            background: rgba(99, 102, 241, 0.15) !important;
            color: var(--primary-light) !important;
            font-weight: 600;
            box-shadow: inset 0 -2px 0 0 var(--primary);
        }

        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            display: none;
        }

        [data-testid="stTabs"] [data-baseweb="tab-border"] {
            display: none;
        }

        /* ── Streamlit Metric Styling ────────────────────────────── */
        [data-testid="stMetric"] {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1rem;
        }

        [data-testid="stMetric"] label {
            color: var(--text-muted) !important;
            font-family: var(--font-main) !important;
            text-transform: uppercase;
            font-size: 0.72rem !important;
            letter-spacing: 1px;
        }

        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-family: var(--font-main) !important;
            font-weight: 700;
        }

        [data-testid="stMetric"] [data-testid="stMetricDelta"] > div {
            font-family: var(--font-main) !important;
            font-weight: 500;
        }

        /* ── Scrollbar ───────────────────────────────────────────── */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.3);
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.5);
        }

        /* ── Fade-in Animation ───────────────────────────────────── */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in {
            animation: fadeInUp 0.5s ease forwards;
        }

        /* ── Summary Grid (batch) ────────────────────────────────── */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }

        /* ── Table / Dataframe Container ─────────────────────────── */
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            border-radius: var(--radius-md) !important;
            overflow: hidden;
            border: 1px solid var(--border-subtle);
        }

        [data-testid="stDataFrame"] [data-testid="glideDataEditor"],
        [data-testid="stDataFrame"] table {
            font-family: var(--font-main) !important;
            font-size: 0.85rem;
        }

        /* ── Buttons ─────────────────────────────────────────────── */
        .stButton > button {
            font-family: var(--font-main) !important;
            font-weight: 600;
            border-radius: var(--radius-sm);
            transition: var(--transition-default);
        }

        .stDownloadButton > button {
            font-family: var(--font-main) !important;
            font-weight: 600;
            border-radius: var(--radius-sm);
        }

        /* ── Expander ────────────────────────────────────────────── */
        [data-testid="stExpander"] {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden;
        }

        [data-testid="stExpander"] summary {
            font-family: var(--font-main) !important;
            font-weight: 600;
            color: var(--text-primary);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
