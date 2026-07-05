import plotly.graph_objects as go
from plotly.subplots import make_subplots

COLORS = {
    "temp":  {"line": "#f97316", "fill": "rgba(249,115,22,0.1)",  "marker": "#fb923c"},
    "vib":   {"line": "#8b5cf6", "fill": "rgba(139,92,246,0.1)",  "marker": "#a78bfa"},
    "pres":  {"line": "#06b6d4", "fill": "rgba(6,182,212,0.1)",   "marker": "#22d3ee"},
}

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

def create_forecast_chart(time_future, temp_pred, vib_pred, pres_pred):
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
                x=time_future, y=pred,
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

    fig.update_xaxes(title_text="Jam ke-", row=3, col=1)
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

def create_combined_chart(time_future, temp_pred, vib_pred, pres_pred):
    fig = go.Figure()

    # Temperature → y1 (left)
    fig.add_trace(go.Scatter(
        x=time_future, y=temp_pred,
        mode="lines+markers",
        name="Temperature",
        line=dict(color=COLORS["temp"]["line"], width=2.5, shape="spline"),
        marker=dict(color=COLORS["temp"]["marker"], size=6),
        yaxis="y",
        hovertemplate="%{y:.2f} °C<extra>Temperature</extra>",
    ))

    # Vibration → y2 (right)
    fig.add_trace(go.Scatter(
        x=time_future, y=vib_pred,
        mode="lines+markers",
        name="Vibration",
        line=dict(color=COLORS["vib"]["line"], width=2.5, shape="spline"),
        marker=dict(color=COLORS["vib"]["marker"], size=6),
        yaxis="y2",
        hovertemplate="%{y:.2f} mm/s<extra>Vibration</extra>",
    ))

    # Pressure → y3 (far right)
    fig.add_trace(go.Scatter(
        x=time_future, y=pres_pred,
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
                title="Jam ke-",
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