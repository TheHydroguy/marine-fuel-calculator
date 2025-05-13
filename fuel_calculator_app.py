
import streamlit as st
import pandas as pd
import numpy as np

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
# Streamlit App Interface
# ------------------------
st.set_page_config(page_title="Fuel Cost & Emissions Calculator", layout="wide")
st.title("🚢 Fuel Cost & Emissions Calculator")
st.markdown("Compare daily fuel cost, burn rate, and emissions across marine fuel types.")

col1, col2, col3 = st.columns(3)

with col1:
    ship_power = st.number_input("Ship Power (MW)", min_value=1.0, max_value=100.0, value=60.0, step=1.0)

with col2:
    operation_hours = st.number_input("Operation Hours per Day", min_value=1, max_value=24, value=24)

with col3:
    selected_fuel = st.selectbox("Select Fuel Type", list(fuel_data.keys()))

# ------------------------
# Calculation Logic
# ------------------------
energy_MJ_day = ship_power * 1e3 * operation_hours  # MW to kW to MJ
fuel_LHV = fuel_data[selected_fuel]["LHV"]
fuel_price = fuel_data[selected_fuel]["Price"]
fuel_CI = fuel_data[selected_fuel]["CI"]

burn_rate = energy_MJ_day / (fuel_LHV * 1e3)  # tons/day
daily_cost = burn_rate * fuel_price
daily_emissions = energy_MJ_day * fuel_CI / 1e6  # tons CO2e/day

# ------------------------
# Output Display
# ------------------------
st.subheader("📊 Results")

st.metric(label="Fuel Burn Rate (tons/day)", value=f"{burn_rate:.2f}")
st.metric(label="Daily Fuel Cost ($/day)", value=f"${daily_cost:,.0f}")
st.metric(label="CO₂e Emissions (tons/day)", value=f"{daily_emissions:.2f}")

st.markdown("---")
st.markdown("### 🔍 Fuel Properties")
st.json(fuel_data[selected_fuel])
