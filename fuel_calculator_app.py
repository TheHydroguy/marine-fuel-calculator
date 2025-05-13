import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
st.set_page_config(page_title="Marine Fuel Calculator", layout="wide")
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .block-container {
            padding-top: 2rem;
        }
        .metric-label, .metric-value {
            font-size: 1.2rem;
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center;'>🚢 Marine Fuel Cost & Emissions Calculator</h1>
    <p style='text-align: center;'>Model fuel cost, burn rate, and emissions across marine fuel types with projected 2028 values.</p>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    ship_power = st.number_input("🔧 Ship Power (MW)", min_value=1.0, max_value=100.0, value=60.0, step=1.0)

with col2:
    operation_hours = st.number_input("⏱️ Operation Hours per Day", min_value=1, max_value=24, value=24)

with col3:
    selected_fuel = st.selectbox("🛢️ Select Fuel Type", list(fuel_data.keys()))

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
st.markdown("---")
st.subheader("📊 Results Summary")

col_a, col_b, col_c = st.columns(3)
col_a.metric(label="Fuel Burn Rate (tons/day)", value=f"{burn_rate:.2f}")
col_b.metric(label="Daily Fuel Cost ($/day)", value=f"${daily_cost:,.0f}")
col_c.metric(label="CO₂e Emissions (tons/day)", value=f"{daily_emissions:.2f}")

st.markdown("---")

# ------------------------
# Visualization Tabs
# ------------------------
tab1, tab2, tab3 = st.tabs(["💸 Cost vs Fuel", "🌍 Emissions vs Fuel", "⚙️ Burn Rate vs Fuel"])

with tab1:
    st.subheader("Fuel Cost Comparison")
    cost_df = pd.DataFrame({
        'Fuel': list(fuel_data.keys()),
        'Daily Cost ($)': [
            (energy_MJ_day / (fuel_data[f]['LHV'] * 1e3)) * fuel_data[f]['Price']
            for f in fuel_data
        ]
    })
    fig1, ax1 = plt.subplots()
    ax1.barh(cost_df['Fuel'], cost_df['Daily Cost ($)'], color="#4e79a7")
    ax1.set_xlabel("$ per Day")
    st.pyplot(fig1)

with tab2:
    st.subheader("CO₂e Emissions by Fuel")
    emissions_df = pd.DataFrame({
        'Fuel': list(fuel_data.keys()),
        'CO₂e Emissions (tons/day)': [
            energy_MJ_day * fuel_data[f]['CI'] / 1e6
            for f in fuel_data
        ]
    })
    fig2, ax2 = plt.subplots()
    ax2.barh(emissions_df['Fuel'], emissions_df['CO₂e Emissions (tons/day)'], color="#59a14f")
    ax2.set_xlabel("Tons CO₂e per Day")
    st.pyplot(fig2)

with tab3:
    st.subheader("Burn Rate by Fuel")
    burn_df = pd.DataFrame({
        'Fuel': list(fuel_data.keys()),
        'Burn Rate (tons/day)': [
            energy_MJ_day / (fuel_data[f]['LHV'] * 1e3)
            for f in fuel_data
        ]
    })
    fig3, ax3 = plt.subplots()
    ax3.barh(burn_df['Fuel'], burn_df['Burn Rate (tons/day)'], color="#f28e2b")
    ax3.set_xlabel("Tons per Day")
    st.pyplot(fig3)

st.markdown("---")
st.caption("Developed using Streamlit • Fuel prices and CI values reflect 2028 projections.")
