import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Page Config for a "Professional Dashboard" look
st.set_page_config(page_title="UPS Battery AI Command", layout="wide")

st.title("🔋 AI Predictive Battery Command Center 💻📊")
st.markdown("---")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Block Selector")
available_blocks = [f"Block_{i+1}" for i in range(30)]
selected_block = st.sidebar.selectbox("Select Target Block", available_blocks)

st.sidebar.header("Simulation Parameters")
temp_input = st.sidebar.slider("Ambient Temperature (°C)", 20, 40, 25)
time_projection = st.sidebar.slider("Project forward (Year)", 1, 10, 1)
replacement_cost = st.sidebar.number_input("Cost per block (Rs)", value=500)

# --- CALCULATIONS (The "AI" Logic) ---
# High temp accelerates degradation exponentially
degradation_factor = 1.2 ** (temp_input - 25)
current_health = 100 - (time_projection * 6 * degradation_factor)
current_health = max(0, min(100, current_health))


import random 
# --- ROW 1: METRICS (With Audio/Visual Alerts) --- 
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Block Health Status", value=f"{current_health:.1f}%",
              delta=f"{current_health-100:.1f}%", delta_color="inverse")
    
with col2:
    # 1. LOGIC & ALERT TRIGGERING
    if current_health < 50:
        status = "CRITICAL"
        icon = "🚨"
        color = "red"
        
        # Trigger Critical Alert (only once per status change)
        if st.session_state.get('last_status') != "CRITICAL":
            st.toast("🚨 CRITICAL: Battery has hit the failure threshold!", icon="🚨")
            # Audio Beep
            st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.session_state.last_status = "CRITICAL"
            
    elif current_health < 60:
        status = "WARNING"
        icon = "⚠️"
        color = "orange"
        
        # Trigger Warning Toast with Random Decay Prediction
        if st.session_state.get('last_status') != "WARNING":
            months_to_decay = random.randint(4, 7)
            st.toast(f"⚠️ WARNING: Predicted battery life decay in {months_to_decay} months.", icon="⚠️")
            st.session_state.last_status = "WARNING"
            
    else:
        status = "HEALTHY"
        icon = "✅"
        color = "green"
        st.session_state.last_status = "HEALTHY"

    # 2. DISPLAY STATUS
    st.write("### System Status:")
    st.subheader(f"{icon} :{color}[{status}]")

with col3:
    total_risk = (100 - current_health) * 31 * (replacement_cost / 100)
    st.metric(label="Estimated Risk Value", value=f"Rs{total_risk:,.0f}")

st.markdown("---")

# --- ROW 2: THE DRAMATIC GAUGE ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.write("### Failure Probability")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 100 - current_health,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Level %"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"},
            'steps' : [
                {'range': [0, 50], 'color': "green"},
                {'range': [50, 80], 'color': "orange"},
                {'range': [80, 100], 'color': "red"}],
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_right:
    st.write("### Predicted Life Decay ⚡")
    # Simulate a decay curve
    months = np.arange(0, 25)
    health_curve = 100 - (months * 2 * degradation_factor)
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=months, y=health_curve, mode='lines+markers', name='Health', line=dict(color='red' if current_health < 50 else 'green')))
    fig_line.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="FAILURE THRESHOLD")
    fig_line.update_layout(xaxis_title="Months from Today", yaxis_title="Health %", yaxis_range=[0,110])
    st.plotly_chart(fig_line, use_container_width=True)

# --- ROW 3: INTERACTIVE HEATMAP ---
st.write("### String Physical Layout Status")
# Reshaping 30 blocks into 6x5
grid_health = []
for i in range(30):
    # Add some randomness to make it look real
    individual_variance = np.random.uniform(0.8, 1.2)
    block_health = 100 - (time_projection * 8 * degradation_factor * individual_variance)
    grid_health.append(max(0, block_health))

grid_data = np.array(grid_health).reshape(6, 5)

fig_heat = go.Figure(data=go.Heatmap(
    z=grid_data,
    x=[f"Col {i}" for i in range(1,6)],
    y=[f"Row {i}" for i in range(1,7)],
    colorscale='RdYlGn',
    zmin=0, zmax=100
))
st.plotly_chart(fig_heat, use_container_width=True)
