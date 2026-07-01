import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Color palette ────────────────────────────────────────────────────────────
COLORS = {
    "temp":  {"line": "#f97316", "fill": "rgba(249,115,22,0.1)",  "marker": "#fb923c"},
    "vib":   {"line": "#8b5cf6", "fill": "rgba(139,92,246,0.1)",  "marker": "#a78bfa"},
    "pres":  {"line": "#06b6d4", "fill": "rgba(6,182,212,0.1)",   "marker": "#22d3ee"},
}

# ── Common layout helpers ────────────────────────────────────────────────────
_FONT = dict(family="Inter, sans-serif", size=13, color="#e2e8f0")
_HOVERLABEL = dict(
    bgcolor="rgba(15,15,26,0.95)",
    font_size=13,
    font_family="Inter",
    bordercolor="rgba(99,102,241,0.5)",
)
_GRID_COLOR = "rgba(99,102,241,0.08)"


def _base_layout(**overrides):
    """Return a dict of layout properties shared by every chart."""
    base = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=_FONT,
        hoverlabel=_HOVERLABEL,
        margin=dict(l=60, r=60, t=60, b=60),
    )
    base.update(overrides)
    return base


def _style_axis(fig, row_col_pairs=None):
    """Apply grid colour to every axis present in *fig*."""
    fig.update_xaxes(gridcolor=_GRID_COLOR, zeroline=False)
    fig.update_yaxes(gridcolor=_GRID_COLOR, zeroline=False)


# ═════════════════════════════════════════════════════════════════════════════
# 1.  Forecast chart  –  3‑row subplots (shared x‑axis)
# ═════════════════════════════════════════════════════════════════════════════
def create_forecast_chart(steps, temp_pred, vib_pred, pres_pred):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=(
            "🌡️ Prediksi Suhu (Temperature_c)",
            "📳 Prediksi Getaran (Vibration_mm_s)",
            "🔵 Prediksi Tekanan (Pressure_bar)",
        ),
    )

    traces = [
        (temp_pred, "Temperature_c", "°C",  1),
        (vib_pred,  "Vibration_mm_s",   "mm/s", 2),
        (pres_pred, "Pressure_bar",    "bar",  3),
    ]

    # Add a purple vertical line at x=1 in all subplots to match the reference
    for i in range(1, 4):
        fig.add_vline(x=1, line_width=2, line_color="purple", row=i, col=1)

    for pred, name, unit, row in traces:
        fig.add_trace(
            go.Scatter(
                x=steps, y=pred,
                mode="lines+markers",
                name="Future Forecast (24 Jam)",
                line=dict(color="red", width=2, shape="linear"),
                marker=dict(color="red", size=5),
                hovertemplate=f"%{{y:.2f}} {unit}<extra>{name}</extra>",
                showlegend=(row == 1), # Only show legend once
            ),
            row=row, col=1,
        )
        fig.update_yaxes(title_text=name, row=row, col=1, gridcolor="rgba(99,102,241,0.08)", zeroline=False)
        fig.update_xaxes(gridcolor="rgba(99,102,241,0.08)", row=row, col=1, zeroline=False)

    # Add a dummy trace for the purple line to show in legend
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode="lines",
            name="Titik Waktu Sekarang (Present)",
            line=dict(color="purple", width=2),
        ),
        row=1, col=1
    )

    fig.update_xaxes(title_text="Step ke-", row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#e2e8f0"),
        height=900,
        margin=dict(l=60, r=200, t=60, b=60), # Extra right margin for legend
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02, # Legend on the right
            bgcolor="rgba(15,15,26,0.8)",
            bordercolor="rgba(99,102,241,0.5)",
            borderwidth=1
        ),
    )
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# 2.  Combined chart  –  single chart, 3 y‑axes
# ═════════════════════════════════════════════════════════════════════════════
def create_combined_chart(steps, temp_pred, vib_pred, pres_pred):
    fig = go.Figure()

    # Temperature → y1 (left)
    fig.add_trace(go.Scatter(
        x=steps, y=temp_pred,
        mode="lines+markers",
        name="Temperature",
        line=dict(color=COLORS["temp"]["line"], width=2.5, shape="spline"),
        marker=dict(color=COLORS["temp"]["marker"], size=6),
        yaxis="y",
        hovertemplate="%{y:.2f} °C<extra>Temperature</extra>",
    ))

    # Vibration → y2 (right)
    fig.add_trace(go.Scatter(
        x=steps, y=vib_pred,
        mode="lines+markers",
        name="Vibration",
        line=dict(color=COLORS["vib"]["line"], width=2.5, shape="spline"),
        marker=dict(color=COLORS["vib"]["marker"], size=6),
        yaxis="y2",
        hovertemplate="%{y:.2f} mm/s<extra>Vibration</extra>",
    ))

    # Pressure → y3 (far right)
    fig.add_trace(go.Scatter(
        x=steps, y=pres_pred,
        mode="lines+markers",
        name="Pressure",
        line=dict(color=COLORS["pres"]["line"], width=2.5, shape="spline"),
        marker=dict(color=COLORS["pres"]["marker"], size=6),
        yaxis="y3",
        hovertemplate="%{y:.2f} bar<extra>Pressure</extra>",
    ))

    fig.update_layout(
        **_base_layout(
            height=500,
            xaxis=dict(
                title="Step ke-",
                gridcolor=_GRID_COLOR,
                zeroline=False,
                domain=[0, 0.9],
            ),
            yaxis=dict(
                title=dict(text="°C", font=dict(color=COLORS["temp"]["line"])),
                gridcolor=_GRID_COLOR,
                zeroline=False,
                tickfont=dict(color=COLORS["temp"]["line"]),
            ),
            yaxis2=dict(
                title=dict(text="mm/s", font=dict(color=COLORS["vib"]["line"])),
                overlaying="y",
                side="right",
                gridcolor=_GRID_COLOR,
                zeroline=False,
                tickfont=dict(color=COLORS["vib"]["line"]),
            ),
            yaxis3=dict(
                title=dict(text="bar", font=dict(color=COLORS["pres"]["line"])),
                overlaying="y",
                side="right",
                position=0.95,
                gridcolor=_GRID_COLOR,
                zeroline=False,
                tickfont=dict(color=COLORS["pres"]["line"]),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
            ),
        )
    )
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# 3.  Heatmap  –  correlation matrix
# ═════════════════════════════════════════════════════════════════════════════
def create_heatmap_chart(df_pred):
    corr = df_pred[["temperature", "vibration", "pressure_bar"]].corr()
    labels = ["Temperature", "Vibration", "Pressure"]

    text_vals = np.around(corr.values, decimals=3).astype(str)

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=labels,
            y=labels,
            colorscale="Viridis",
            zmin=-1,
            zmax=1,
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=14, color="#e2e8f0"),
            hovertemplate="(%{x}, %{y}): %{z:.3f}<extra></extra>",
            colorbar=dict(
                title=dict(text="Korelasi", font=dict(color="#e2e8f0")),
                tickfont=dict(color="#e2e8f0"),
            ),
        )
    )

    fig.update_layout(
        **_base_layout(
            height=400,
            xaxis=dict(tickfont=dict(color="#e2e8f0")),
            yaxis=dict(tickfont=dict(color="#e2e8f0"), autorange="reversed"),
        )
    )
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# 4.  Batch overview  –  bar chart with threshold lines
# ═════════════════════════════════════════════════════════════════════════════
def _threshold_color(value, warning, danger):
    """Return green / amber / red based on threshold."""
    if value >= danger:
        return "#ef4444"
    if value >= warning:
        return "#f59e0b"
    return "#10b981"


def create_batch_overview_chart(all_results, thresholds):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.2,
        subplot_titles=(
            "🌡️ Maks Temperature per Data",
            "📳 Maks Vibration per Data",
            "🔵 Maks Pressure per Data",
        ),
    )

    n = len(all_results)
    x_labels = [f"{i+1}" for i in range(n)]

    configs = [
        ("max_temp", "temp", "°C",  1),
        ("max_vib",  "vib",  "mm/s", 2),
        ("max_pres", "pres", "bar",  3),
    ]

    for key, thr_key, unit, row in configs:
        values = [r[key] for r in all_results]
        warn = thresholds[thr_key]["warning"]
        dang = thresholds[thr_key]["danger"]

        bar_colors = [_threshold_color(v, warn, dang) for v in values]

        fig.add_trace(
            go.Bar(
                x=x_labels,
                y=values,
                marker_color=bar_colors,
                hovertemplate=f"Data %{{x}}: %{{y:.2f}} {unit}<extra></extra>",
                showlegend=False,
            ),
            row=row, col=1,
        )

        # Warning line (amber dashed)
        fig.add_hline(
            y=warn, row=row, col=1,
            line=dict(color="#f59e0b", width=1.5, dash="dash"),
            opacity=0.5,
            annotation_text=f"Warning ({warn})",
            annotation_font=dict(color="#f59e0b", size=11),
            annotation_position="top right",
        )
        # Danger line (red dashed)
        fig.add_hline(
            y=dang, row=row, col=1,
            line=dict(color="#ef4444", width=1.5, dash="dash"),
            opacity=0.5,
            annotation_text=f"Danger ({dang})",
            annotation_font=dict(color="#ef4444", size=11),
            annotation_position="top right",
        )

        fig.update_yaxes(title_text=unit, row=row, col=1)

    fig.update_xaxes(title_text="Data ke-", row=3, col=1)

    fig.update_layout(
        **_base_layout(
            height=850,
            margin=dict(l=60, r=60, t=80, b=60),
            showlegend=False,
        )
    )
    _style_axis(fig)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# 5.  Risk donut chart
# ═════════════════════════════════════════════════════════════════════════════
def create_risk_donut_chart(n_safe, n_warning, n_danger):
    total = n_safe + n_warning + n_danger
    labels = ["Aman (Safe)", "Peringatan (Warning)", "Bahaya (Danger)"]
    values = [n_safe, n_warning, n_danger]
    colors = ["#10b981", "#f59e0b", "#ef4444"]

    fig = go.Figure(
        data=go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0.3)", width=2)),
            textinfo="percent",
            textposition="inside",
            textfont=dict(size=14, color="#e2e8f0", family="Inter, sans-serif"),
            hovertemplate="%{label}: %{value} data (%{percent})<extra></extra>",
            sort=False,
        )
    )

    fig.update_layout(
        **_base_layout(
            height=380,
            margin=dict(l=10, r=10, t=30, b=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5,
                font=dict(color="#e2e8f0"),
            ),
            annotations=[
                dict(
                    text=f"<b>{total}</b><br>Total",
                    x=0.5, y=0.5,
                    font=dict(size=22, color="#e2e8f0", family="Inter, sans-serif"),
                    showarrow=False,
                )
            ],
        )
    )
    return fig
