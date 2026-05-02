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
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=parameter,
        height=height,
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=50, r=20, t=50, b=50)
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
        hole=0.4,
        marker=dict(
            colors=['#28a745', '#ffc107', '#dc3545', '#6c757d']
        )
    )])
    
    fig.update_layout(
        title="Status Distribution",
        height=350,
        showlegend=True,
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
        x=confidences,
        nbinsx=20,
        marker=dict(color='#1f77b4'),
        opacity=0.7
    )])
    
    fig.update_layout(
        title="Confidence Score Distribution",
        xaxis_title="Confidence",
        yaxis_title="Count",
        height=300,
        template='plotly_white',
        margin=dict(l=50, r=20, t=50, b=50)
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
            colorscale='Viridis',
            showscale=True
        )
    )])
    
    fig.update_layout(
        title=f"Top {top_n} Feature Importance",
        xaxis_title="Importance",
        yaxis_title="Feature",
        height=400,
        template='plotly_white',
        margin=dict(l=200, r=20, t=50, b=50)
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
        title=title,
        xaxis_title="Time",
        yaxis_title="Value",
        height=400,
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=50, r=20, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
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
    Render process stage summary cards
    
    Args:
        data: Process data dictionary
    """
    stages = {
        "Die Attach": ["die_temperature", "die_void_percentage", "die_placement_accuracy"],
        "Wire Bonding": ["wire_bonding_force", "wire_pull_strength", "wire_loop_height"],
        "Molding": ["mold_temperature", "mold_pressure", "mold_voids"],
        "Curing": ["cure_temperature", "cure_uniformity", "cure_time"],
        "Inspection": ["inspect_reliability_score", "inspect_defect_count", "inspect_visual_score"]
    }
    
    cols = st.columns(5)
    
    for idx, (stage_name, params) in enumerate(stages.items()):
        with cols[idx]:
            st.markdown(f"**{stage_name}**")
            
            # Calculate stage health (simplified)
            param_values = [data.get(p, 0) for p in params if p in data]
            if param_values:
                avg_value = sum(param_values) / len(param_values)
                health = "✓" if avg_value > 50 else "⚠"
                color = "green" if avg_value > 50 else "orange"
            else:
                health = "?"
                color = "gray"
            
            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    font-size: 40px;
                    color: {color};
                    padding: 10px;
                ">
                    {health}
                </div>
                """,
                unsafe_allow_html=True
            )


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
