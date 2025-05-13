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

# ------------------------
# Streamlit Setup
# ------------------------
st.set_page_config(page_title="Marine Fuel Calculator", layout="wide")
st.title("🚢 Marine Fuel Cost & Emissions Calculator")

col1, col2, col3 = st.columns(3)

with col1:
    ship_power = st.number_input("Ship Power (MW)", min_value=1.0, max_value=100.0, value=60.0)

with col2:
    operation_hours = st.number_input("Operation Hours per Day", min_value=1, max_value=24, value=24)

with col3:
    selected_fuel = st.selectbox("Select Fuel Type", list(fuel_data.keys()))

# ------------------------
# Calculations
# ------------------------
energy_MJ_day = ship_power * 1e3 * operation_hours
fuel_LHV = fuel_data[selected_fuel]["LHV"]
fuel_price = fuel_data[selected_fuel]["Price"]
fuel_CI = fuel_data[selected_fuel]["CI"]

burn_rate = energy_MJ_day / (fuel_LHV * 1e3)
daily_cost = burn_rate * fuel_price
daily_emissions = energy_MJ_day * fuel_CI / 1e6

# ------------------------
# Display Results
# ------------------------
st.markdown("---")
st.subheader("📊 Results Summary")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Fuel Burn Rate (tons/day)", f"{burn_rate:.2f}")
col_b.metric("Daily Fuel Cost ($/day)", f"${daily_cost:,.0f}")
col_c.metric("CO₂e Emissions (tons/day)", f"{daily_emissions:.2f}")
st.markdown("---")

# ------------------------
# Tabs with Plotly Charts
# ------------------------
tab1, tab2, tab3 = st.tabs(["💸 Cost Sensitivity", "🌍 Emissions", "⚙️ Burn Rate"])

# Tab 1 - Cost Sensitivity
with tab1:
    prices = np.linspace(200, 1200, 6)
    fig = go.Figure()
    for fuel in fuel_data:
        lhv = fuel_data[fuel]['LHV']
        burn = energy_MJ_day / (lhv * 1e3)
        daily_costs = burn * prices
        fig.add_trace(go.Scatter(x=prices, y=daily_costs, mode='lines', name=fuel))
    fig.update_layout(
        title="Daily Cost vs Fuel Price",
        xaxis_title="Fuel Price ($/ton)",
        yaxis_title="Daily Cost ($)",
        height=400,
        width=700,
        template="plotly_white",
        legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center", font=dict(size=9))
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 2 - Emissions
with tab2:
    emissions = {
        fuel: energy_MJ_day * fuel_data[fuel]["CI"] / 1e6
        for fuel in fuel_data
    }
    fig2 = go.Figure([go.Bar(x=list(emissions.keys()), y=list(emissions.values()))])
    fig2.update_layout(
        title="CO₂e Emissions per Fuel (tons/day)",
        xaxis_title="Fuel",
        yaxis_title="Emissions (tons/day)",
        height=400,
        width=700,
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Tab 3 - Burn Rate
with tab3:
    burns = {
        fuel: energy_MJ_day / (fuel_data[fuel]["LHV"] * 1e3)
        for fuel in fuel_data
    }
    fig3 = go.Figure([go.Bar(x=list(burns.keys()), y=list(burns.values()))])
    fig3.update_layout(
        title="Fuel Burn Rate (tons/day)",
        xaxis_title="Fuel",
        yaxis_title="Burn Rate (tons/day)",
        height=400,
        width=700,
        template="plotly_white"
    )
    st.plotly_chart(fig3, use_container_width=True)
