"""
Charts Component for AI Packaging Reliability Copilot Dashboard
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Optional


def render_parameter_gauge(
    parameter_name: str,
    value: float,
    min_val: float,
    max_val: float,
    warning_threshold: float,
    severe_threshold: float,
    unit: str = ""
) -> None:
    """
    Render parameter gauge chart
    
    Args:
        parameter_name: Parameter name
        value: Current value
        min_val: Minimum value
        max_val: Maximum value
        warning_threshold: Warning threshold
        severe_threshold: Severe threshold
        unit: Unit of measurement
    """
    # Determine color based on thresholds
    if value >= severe_threshold or value <= (min_val + (max_val - min_val) * 0.1):
        color = "red"
    elif value >= warning_threshold or value <= (min_val + (max_val - min_val) * 0.2):
        color = "orange"
    else:
        color = "green"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{parameter_name} ({unit})", 'font': {'size': 16}},
        delta={'reference': (min_val + max_val) / 2},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_val, warning_threshold], 'color': 'lightgreen'},
                {'range': [warning_threshold, severe_threshold], 'color': 'lightyellow'},
                {'range': [severe_threshold, max_val], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': severe_threshold
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'size': 12}
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_time_series(
    data: pd.DataFrame,
    parameter: str,
    title: str = "Parameter Trend",
    height: int = 400
) -> None:
    """
    Render time series chart
    
    Args:
        data: DataFrame with timestamp and parameter columns
        parameter: Parameter name to plot
        title: Chart title
        height: Chart height
    """
    if data.empty or parameter not in data.columns:
        st.warning(f"No data available for {parameter}")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['timestamp'],
        y=data[parameter],
        mode='lines+markers',
        name=parameter,
        line=dict(color='#4d94ff', width=2),
        marker=dict(size=5, color='#0f62fe')
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color='#1a2238')),
        xaxis=dict(title='Time', color='#697077', gridcolor='#dde6ff'),
        yaxis=dict(title=parameter, color='#697077', gridcolor='#dde6ff'),
        height=height, hovermode='x unified',
        paper_bgcolor='rgba(248,250,255,1)',
        plot_bgcolor='rgba(248,250,255,1)',
        margin=dict(l=50, r=20, t=50, b=50),
        font=dict(color='#1a2238')
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_status_distribution(predictions: List[Dict]) -> None:
    """
    Render status distribution pie chart
    
    Args:
        predictions: List of predictions with status
    """
    if not predictions:
        st.info("No prediction data available")
        return
    
    # Count status occurrences
    status_counts = {}
    for pred in predictions:
        status = pred.get('predicted_status', 'UNKNOWN')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(status_counts.keys()),
        values=list(status_counts.values()),
        hole=0.45,
        marker=dict(colors=['#42be65', '#f1c21b', '#fa4d56', '#8aa3cc']),
        textfont=dict(color='white', size=13)
    )])
    fig.update_layout(
        title=dict(text='Status Distribution', font=dict(color='#1a2238')),
        height=350, showlegend=True,
        paper_bgcolor='rgba(248,250,255,1)',
        font=dict(color='#1a2238'),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_confidence_histogram(predictions: List[Dict]) -> None:
    """
    Render confidence score histogram
    
    Args:
        predictions: List of predictions with confidence
    """
    if not predictions:
        st.info("No prediction data available")
        return
    
    confidences = [p.get('confidence', 0) for p in predictions if 'confidence' in p]
    
    if not confidences:
        st.warning("No confidence data available")
        return
    
    fig = go.Figure(data=[go.Histogram(
        x=confidences, nbinsx=20,
        marker=dict(color='#0f62fe', opacity=0.8),
        name='Confidence'
    )])
    fig.update_layout(
        title=dict(text='Confidence Score Distribution', font=dict(color='#1a2238')),
        xaxis=dict(title='Confidence', color='#697077', gridcolor='#dde6ff'),
        yaxis=dict(title='Count', color='#697077', gridcolor='#dde6ff'),
        height=300,
        paper_bgcolor='rgba(248,250,255,1)',
        plot_bgcolor='rgba(248,250,255,1)',
        margin=dict(l=50, r=20, t=50, b=50),
        font=dict(color='#1a2238')
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_feature_importance(features: List[Dict], top_n: int = 10) -> None:
    """
    Render feature importance bar chart
    
    Args:
        features: List of features with importance scores
        top_n: Number of top features to show
    """
    if not features:
        st.info("No feature importance data available")
        return
    
    # Sort by importance and take top N
    sorted_features = sorted(features, key=lambda x: x.get('importance', 0), reverse=True)[:top_n]
    
    names = [f['feature'] for f in sorted_features]
    importances = [f['importance'] for f in sorted_features]
    
    fig = go.Figure(data=[go.Bar(
        x=importances,
        y=names,
        orientation='h',
        marker=dict(
            color=importances,
            colorscale=[[0,'#0043ce'],[0.5,'#0f62fe'],[1,'#198038']],
            showscale=True,
            colorbar=dict(title='Importance', tickfont=dict(color='#1a2238'))
        )
    )])
    fig.update_layout(
        title=dict(text=f'Top {top_n} Feature Importance', font=dict(color='#1a2238')),
        xaxis=dict(title='Importance', color='#697077', gridcolor='#dde6ff'),
        yaxis=dict(title='Feature', color='#697077'),
        height=420,
        paper_bgcolor='rgba(248,250,255,1)',
        plot_bgcolor='rgba(248,250,255,1)',
        margin=dict(l=200, r=20, t=50, b=50),
        font=dict(color='#1a2238')
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_multi_parameter_chart(
    data: pd.DataFrame,
    parameters: List[str],
    title: str = "Multi-Parameter Trend"
) -> None:
    """
    Render multiple parameters on same chart
    
    Args:
        data: DataFrame with timestamp and parameter columns
        parameters: List of parameter names
        title: Chart title
    """
    if data.empty:
        st.warning("No data available")
        return
    
    fig = go.Figure()
    
    for param in parameters:
        if param in data.columns:
            fig.add_trace(go.Scatter(
                x=data['timestamp'],
                y=data[param],
                mode='lines',
                name=param,
                line=dict(width=2)
            ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(color='#1a2238')),
        xaxis=dict(title='Time', color='#697077', gridcolor='#dde6ff'),
        yaxis=dict(title='Value', color='#697077', gridcolor='#dde6ff'),
        height=400, hovermode='x unified',
        paper_bgcolor='rgba(248,250,255,1)',
        plot_bgcolor='rgba(248,250,255,1)',
        margin=dict(l=50, r=20, t=50, b=50),
        font=dict(color='#1a2238'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_correlation_heatmap(data: pd.DataFrame, parameters: List[str]) -> None:
    """
    Render correlation heatmap
    
    Args:
        data: DataFrame with parameters
        parameters: List of parameter names
    """
    if data.empty:
        st.warning("No data available")
        return
    
    # Select only numeric columns that exist
    available_params = [p for p in parameters if p in data.columns]
    
    if len(available_params) < 2:
        st.warning("Not enough parameters for correlation analysis")
        return
    
    # Calculate correlation
    corr_matrix = data[available_params].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Parameter Correlation Matrix",
        height=500,
        margin=dict(l=100, r=20, t=50, b=100)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_process_stage_summary(data: Dict) -> None:
    """
    Render process stage health flow with scored cards.
    """
    # Stage definitions: (display name, params, normal ranges)
    STAGE_DEF = {
        "Die Attach":    [("die_temperature",170,200),("die_void_percentage",0,3),("die_placement_accuracy",0,10)],
        "Wire Bonding":  [("wire_bonding_force",35,55),("wire_pull_strength",6,15),("wire_loop_height",190,250)],
        "Molding":       [("mold_temperature",168,182),("mold_pressure",5,10),("mold_voids",0,1)],
        "Curing":        [("cure_temperature",177,188),("cure_uniformity",1,2),("cure_time",120,180)],
        "Inspection":    [("inspect_reliability_score",90,100),("inspect_defect_count",0,0),("inspect_visual_score",90,100)],
    }
    ICONS = ["🔩","🔗","🧱","🔥","🔍"]

    def _stage_score(params):
        scores = []
        for param, lo, hi in params:
            val = data.get(param)
            if val is None:
                continue
            rng = hi - lo if hi != lo else 1
            # Clamp to [lo-rng, hi+rng] then score 0-100
            deviation = max(0, lo - val) + max(0, val - hi)
            sc = max(0.0, 100.0 - (deviation / rng) * 100)
            scores.append(sc)
        return round(sum(scores) / len(scores)) if scores else 50

    names  = list(STAGE_DEF.keys())
    scores = [_stage_score(STAGE_DEF[n]) for n in names]

    # Build HTML flow
    cards_html = ""
    for i, (name, score, icon) in enumerate(zip(names, scores, ICONS)):
        cls = "good" if score >= 85 else ("warning" if score >= 60 else "severe")
        bar_color = {"good":"#42be65","warning":"#f1c21b","severe":"#fa4d56"}[cls]
        arrow = '<div class="flow-arrow">&#8250;</div>' if i < len(names)-1 else ""
        cards_html += f"""
        <div class="flow-card {cls}">
            <div class="flow-icon">{icon}</div>
            <div class="flow-stage">{name}</div>
            <div class="flow-score {cls}">{score}</div>
            <div style="font-size:.6rem;color:#697077;">/ 100</div>
            <div style="background:#dde6ff;border-radius:3px;height:4px;margin-top:5px;">
              <div style="background:{bar_color};width:{score}%;height:4px;border-radius:3px;transition:width .4s;"></div>
            </div>
        </div>{arrow}"""

    st.markdown(f'<div class="flow-wrap">{cards_html}</div>', unsafe_allow_html=True)


def render_stage_health_radar(stage_scores: Dict[str, float]) -> None:
    """Render a radar chart of process stage health scores (0-100)."""
    if not stage_scores:
        st.info("No stage health data available")
        return

    categories = list(stage_scores.keys())
    values = list(stage_scores.values())
    # Close the polygon
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(15,98,254,0.2)',
        line=dict(color='#0f62fe', width=2),
        name='Stage Health',
        hovertemplate='%{theta}: %{r:.0f}<extra></extra>'
    ))
    # Good-zone ring
    fig.add_trace(go.Scatterpolar(
        r=[85] * (len(categories) + 1),
        theta=categories_closed,
        mode='lines',
        line=dict(color='rgba(66,190,101,0.25)', width=1, dash='dot'),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(248,250,255,1)',
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color='#697077', size=9),
                gridcolor='#dde6ff', linecolor='#dde6ff'
            ),
            angularaxis=dict(
                tickfont=dict(color='#1a2238', size=11),
                linecolor='#dde6ff', gridcolor='#dde6ff'
            )
        ),
        title=dict(text='Stage Health Radar', font=dict(color='#1a2238')),
        paper_bgcolor='rgba(248,250,255,1)',
        height=360,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(color='#1a2238'),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_parameter_deviation_heatmap(data: Dict) -> None:
    """
    Render a heatmap showing how far each parameter deviates from its normal range.
    Red = severe deviation, green = within normal.
    """
    # Parameter normal ranges: (min, max)
    PARAM_RANGES = {
        'die_temperature':          (175, 195),
        'die_void_percentage':      (0,   3),
        'die_placement_accuracy':   (0,   10),
        'die_epoxy_temperature':    (145, 165),
        'wire_bonding_force':       (35,  55),
        'wire_pull_strength':       (7,   15),
        'wire_loop_height':         (190, 250),
        'wire_ultrasonic_power':    (80,  100),
        'mold_temperature':         (168, 182),
        'mold_pressure':            (5,   10),
        'mold_voids':               (0,   1),
        'mold_fill_time':           (3,   6),
        'cure_temperature':         (177, 188),
        'cure_uniformity':          (1,   2),
        'cure_time':                (120, 180),
        'inspect_reliability_score':(90,  100),
        'inspect_defect_count':     (0,   0),
        'inspect_visual_score':     (90,  100),
    }

    params, deviations, labels = [], [], []
    for param, (lo, hi) in PARAM_RANGES.items():
        val = data.get(param)
        if val is None:
            continue
        rng = (hi - lo) if hi != lo else 1.0
        dev = max(0.0, lo - val) + max(0.0, val - hi)
        norm_dev = min(100.0, (dev / rng) * 100)
        params.append(param.replace('_', ' ').title())
        deviations.append([norm_dev])
        labels.append(f"{val:.1f}")

    if not params:
        st.info("No parameter data available")
        return

    import numpy as np
    z = np.array(deviations)

    fig = go.Figure(data=go.Heatmap(
        z=z,
        y=params,
        x=['Deviation %'],
        colorscale=[[0,'#198038'],[0.3,'#f1c21b'],[0.7,'#ff832b'],[1,'#da1e28']],
        zmin=0, zmax=100,
        text=[[l] for l in labels],
        texttemplate='%{text}',
        textfont=dict(size=10, color='white'),
        colorbar=dict(title='Dev%', tickfont=dict(color='#1a2238'), title_font=dict(color='#1a2238'))
    ))
    fig.update_layout(
        title=dict(text='Parameter Deviation from Normal Range', font=dict(color='#1a2238')),
        xaxis=dict(color='#697077'),
        yaxis=dict(color='#697077', autorange='reversed', tickfont=dict(size=10)),
        height=max(320, len(params) * 22),
        paper_bgcolor='rgba(248,250,255,1)',
        plot_bgcolor='rgba(248,250,255,1)',
        margin=dict(l=200, r=60, t=50, b=40),
        font=dict(color='#1a2238')
    )
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    # Test charts
    st.set_page_config(page_title="Charts Test", layout="wide")
    
    st.title("Charts Component Test")
    
    # Test gauge
    st.subheader("Parameter Gauge")
    render_parameter_gauge(
        "Temperature",
        185.0,
        170.0,
        200.0,
        190.0,
        195.0,
        "°C"
    )
    
    # Test time series
    st.subheader("Time Series")
    sample_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
        'temperature': [180 + i * 0.1 for i in range(100)]
    })
    render_time_series(sample_data, 'temperature', "Temperature Trend")
    
    # Test status distribution
    st.subheader("Status Distribution")
    sample_predictions = [
        {'predicted_status': 'GOOD', 'confidence': 0.95},
        {'predicted_status': 'GOOD', 'confidence': 0.93},
        {'predicted_status': 'WARNING', 'confidence': 0.78},
        {'predicted_status': 'SEVERE', 'confidence': 0.92},
    ]
    render_status_distribution(sample_predictions)

# Made with Bob
