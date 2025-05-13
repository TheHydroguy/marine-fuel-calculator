from pathlib import Path

# Streamlit + Plotly Final Code (Cost Sensitivity with Clean Chart)
final_code = """
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ------------------------
# Fuel Properties Database
# ------------------------
fuel_data = {
    "VLSFO": {"LHV": 42.7, "Price": 650, "CI": 91},
    "Gray Methanol": {"LHV": 20, "Price": 450, "CI": 85},
    "Green Methanol": {"LHV": 20, "Price": 950, "CI": 10},
    "Gray Ammonia": {"LHV": 18.6, "Price": 700, "CI": 90},
    "Green Ammonia": {"LHV": 18.6, "Price": 1200, "CI": 5},
    "Gray Hydrogen": {"LHV": 120, "Price": 3800, "CI": 90},
    "Green Hydrogen": {"LHV": 120, "Price": 4500, "CI": 3},
    "B30 Blend": {"LHV": 40.1, "Price": 800, "CI": 82.2},
    "FAME Biodiesel": {"LHV": 38, "Price": 1200, "CI": 35}
}

# Streamlit Interface
st.set_page_config(page_title="Marine Fuel Cost & Emissions Calculator", layout="wide")
st.title("🚢 Marine Fuel Cost & Emissions Calculator")

col1, col2, col3 = st.columns(3)

with col1:
    ship_power = st.number_input("Ship Power (MW)", min_value=1.0, max_value=100.0, value=60.0, step=1.0)

with col2:
    operation_hours = st.number_input("Operation Hours per Day", min_value=1, max_value=24, value=24)

with col3:
    selected_fuel = st.selectbox("Select Fuel Type", list(fuel_data.keys()))

# Core Calculations
energy_MJ_day = ship_power * 1e3 * operation_hours
fuel_LHV = fuel_data[selected_fuel]["LHV"]
fuel_price = fuel_data[selected_fuel]["Price"]
fuel_CI = fuel_data[selected_fuel]["CI"]

burn_rate = energy_MJ_day / (fuel_LHV * 1e3)
daily_cost = burn_rate * fuel_price
daily_emissions = energy_MJ_day * fuel_CI / 1e6

# Output Summary
st.markdown("---")
st.subheader("📊 Results Summary")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Fuel Burn Rate (tons/day)", f"{burn_rate:.2f}")
col_b.metric("Daily Fuel Cost ($/day)", f"${daily_cost:,.0f}")
col_c.metric("CO₂e Emissions (tons/day)", f"{daily_emissions:.2f}")
st.markdown("---")

# Plotly Cost Sensitivity Chart
if st.button("Generate Cost Sensitivity Chart"):
    prices = np.linspace(200, 1200, 6)
    fig = go.Figure()
    for fuel in fuel_data:
        lhv = fuel_data[fuel]['LHV']
        burn = energy_MJ_day / (lhv * 1e3)
        daily_costs = burn * prices
        fig.add_trace(go.Scatter(
            x=prices,
            y=daily_costs,
            mode='lines',
            name=fuel,
            line=dict(width=1.5)
        ))

    fig.update_layout(
        title="Daily Cost vs Fuel Price",
        xaxis_title="Fuel Price ($/ton)",
        yaxis_title="Daily Cost ($)",
        template="plotly_white",
        height=400,
        width=650,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        )
    )
    st.plotly_chart(fig, use_container_width=True)
"""

# Write file
file_path = Path("/mnt/data/fuel_cost_plotly_app.py")
file_path.write_text(final_code)
file_path.name
