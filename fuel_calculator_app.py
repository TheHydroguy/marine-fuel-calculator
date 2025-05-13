from pathlib import Path

merged_app_code = """
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
    "Green Methanol": {"LHV": 20, "Price": 950, "CI": 10, "CapEx": 10_000_000, "Infra": 5000},
    "Gray Ammonia": {"LHV": 18.6, "Price": 700, "CI": 90},
    "Green Ammonia": {"LHV": 18.6, "Price": 1200, "CI": 5, "CapEx": 15_000_000, "Infra": 18000},
    "Gray Hydrogen": {"LHV": 120, "Price": 3800, "CI": 90},
    "Green Hydrogen (Fuel Cell)": {"LHV": 120, "Price": 4500, "CI": 3, "eff": 0.55, "CapEx": 25_000_000, "Infra": 22000},
    "B30 Blend": {"LHV": 40.1, "Price": 800, "CI": 82.2},
    "FAME Biodiesel": {"LHV": 38, "Price": 1200, "CI": 35}
}

# ------------------------
# App Config
# ------------------------
st.set_page_config(page_title=\"Marine Fuel App\", layout=\"wide\")

# ------------------------
# Shared Inputs
# ------------------------
st.sidebar.header(\"🛠️ Ship Configuration\")
ship_power = st.sidebar.number_input(\"Ship Power (MW)\", value=60.0, min_value=1.0)
operation_hours = st.sidebar.number_input(\"Operating Hours per Day\", value=24, min_value=1, max_value=24)
energy_MJ_day = ship_power * 1e3 * operation_hours

# ------------------------
# Tabs
# ------------------------
tab1, tab2 = st.tabs([\"🔍 Module 1: Fuel Calculator\", \"💥 Module 2: Switch or Pay\"])

# ------------------------
# Module 1: Fuel Calculator
# ------------------------
with tab1:
    st.header(\"Module 1: Fuel Cost & Emissions Calculator\")
    selected_fuel = st.selectbox(\"Select Fuel Type\", list(fuel_data.keys()))
    props = fuel_data[selected_fuel]
    eff = props.get(\"eff\", 1.0)

    burn_rate = energy_MJ_day / (props[\"LHV\"] * 1e3 * eff)
    daily_cost = burn_rate * props[\"Price\"]
    emissions = energy_MJ_day * props[\"CI\"] / 1e6

    st.metric(\"Burn Rate (t/day)\", f\"{burn_rate:.2f}\")
    st.metric(\"Fuel Cost ($/day)\", f\"${daily_cost:,.0f}\")
    st.metric(\"Emissions (tons CO₂e/day)\", f\"{emissions:.2f}\")

    prices = [400, 800, 1200]
    chart_data = []
    for price in prices:
        cost = burn_rate * price
        chart_data.append({\"Fuel\": selected_fuel, \"Price\": f\"${price}\", \"Cost\": cost})
    df = pd.DataFrame(chart_data)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[\"Price\"], y=df[\"Cost\"], name=selected_fuel))
    fig.update_layout(title=\"Daily Cost at Price Points\", yaxis_title=\"Cost ($/day)\", template=\"plotly_white\")
    st.plotly_chart(fig)

# ------------------------
# Module 2: Switch or Pay
# ------------------------
with tab2:
    st.header(\"Module 2: Switch or Pay Strategy (IMO 2028)\")
    ci_reduction = st.slider(\"CI Reduction Target (%)\", min_value=0, max_value=40, value=4, step=1)
    carbon_fee = st.number_input(\"Carbon Fee ($/ton CO₂e)\", value=380, step=10)

    ci_target = 93.3 * (1 - ci_reduction / 100)
    discount_rate = 0.08
    lifetime = 20
    days_per_year = 365

    def calc_row(name, props):
        eff = props.get(\"eff\", 1.0)
        burn = energy_MJ_day / (props[\"LHV\"] * 1e3 * eff)
        fuel_cost = burn * props[\"Price\"]
        excess_CI = max(props[\"CI\"] - ci_target, 0)
        excess_CO2 = excess_CI * energy_MJ_day / 1e6
        fee = excess_CO2 * carbon_fee
        capex = props.get(\"CapEx\", 0)
        infra = props.get(\"Infra\", 0)
        capex_day = (capex * discount_rate) / (1 - (1 + discount_rate) ** (-lifetime)) / days_per_year
        total = fuel_cost + fee + capex_day + infra
        return {
            \"Fuel\": name,
            \"Burn Rate (t/day)\": round(burn, 2),
            \"Fuel Cost\": round(fuel_cost),
            \"Carbon Fee\": round(fee),
            \"CapEx/day\": round(capex_day),
            \"Infra/day\": infra,
            \"Total Cost\": round(total)
        }

    rows = [calc_row(name, props) for name, props in fuel_data.items()]
    df2 = pd.DataFrame(rows)
    st.metric(\"2028 CI Limit\", f\"{ci_target:.2f} gCO₂e/MJ\")
    st.dataframe(df2.set_index(\"Fuel\"))

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df2[\"Fuel\"], y=df2[\"Total Cost\"], name=\"Total Daily Cost\"))
    fig2.update_layout(title=\"Switch vs Pay: Total Daily Cost\", yaxis_title=\"$/day\", template=\"plotly_white\")
    st.plotly_chart(fig2)
"""

# Write merged app to file
merged_path = Path("/mnt/data/fuel_app_full.py")
merged_path.write_text(merged_app_code)
merged_path.name
