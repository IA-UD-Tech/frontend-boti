"""
Visualization utilities for creating interactive charts.
"""

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def generate_sample_usage_data():
    """
    Generate realistic sample data for usage graphs.
    
    Returns:
        dict: Data for visualization with dates, counts and active students
    """
    today = datetime.now()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    # Create a more realistic pattern with a weekday peak
    base = random.randint(8, 15)
    variance = random.randint(3, 8)
    trend = random.choice([0.8, 1.0, 1.2])  # Downward, neutral, or upward trend

    counts = []
    active_students = []

    for i, date in enumerate(dates):
        # Lower usage on weekends (5 and 6 are weekend indices)
        is_weekend = date.weekday() >= 5
        weekend_factor = 0.4 if is_weekend else 1.0

        # Generate count with some randomness but following a pattern
        day_count = int((base + random.randint(-variance, variance)) * weekend_factor * (trend ** i))
        counts.append(max(1, day_count))  # Ensure at least 1 interaction

        # Generate active students (subset of total students)
        students = random.randint(max(1, day_count // 3), max(2, day_count // 2))
        active_students.append(students)

    return {
        "dates": dates, 
        "counts": counts,
        "active_students": active_students
    }

def create_usage_chart(usage_data):
    """
    Create an interactive usage chart with Plotly.
    
    Args:
        usage_data (dict): Usage data with dates, counts and active students
        
    Returns:
        plotly.graph_objects.Figure: Interactive Plotly figure
    """
    # Create DataFrame from usage data
    usage_df = pd.DataFrame({
        'Fecha': usage_data["dates"],
        'Interacciones': usage_data["counts"],
        'Estudiantes Activos': usage_data["active_students"]
    })
    
    # Create a figure with secondary y-axis
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(
        go.Scatter(
            x=usage_df['Fecha'], 
            y=usage_df['Interacciones'],
            name="Interacciones",
            line=dict(color="#0068c9", width=3),
            mode='lines+markers'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=usage_df['Fecha'], 
            y=usage_df['Estudiantes Activos'],
            name="Estudiantes Activos",
            line=dict(color="#83c9ff", width=2, dash='dot'),
            mode='lines+markers'
        )
    )
    
    # Customize layout
    fig.update_layout(
        title=dict(
            text="Actividad Semanal",
            font=dict(size=16)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        height=250,
        hovermode="x unified",
        xaxis=dict(
            title="",
            showgrid=False
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig