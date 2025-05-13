import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ------------------------
# Fuel Properties Database (Green Hydrogen renamed)
# ------------------------
fuel_data = {
    "VLSFO": {"LHV": 42.7, "Price": 650, "CI": 91},
    "Gray Methanol": {"LHV": 20, "Price": 450, "CI": 85},
    "Green Methanol": {"LHV": 20, "Price": 950, "CI": 10},
    "Gray Ammonia": {"LHV": 18.6, "Price": 700, "CI": 90},
    "Green Ammonia": {"LHV": 18.6, "Price": 1200, "CI": 5},
    "Gray Hydrogen": {"LHV": 120, "Price": 3800, "CI": 90, "eff": 0.55},
    "Green Hydrogen (Fuel Cell)": {"LHV": 120, "Price": 4500, "CI": 3, "eff": 0.55},
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
fuel_props = fuel_data[selected_fuel]
eff = fuel_props.get("eff", 1.0)

burn_rate = energy_MJ_day / (fuel_props["LHV"] * 1e3 * eff)
daily_cost = burn_rate * fuel_props["Price"]
daily_emissions = energy_MJ_day * fuel_props["CI"] / 1e6

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
# Plotly Tabs
# ------------------------
tab1, tab2, tab3 = st.tabs(["💸 Cost Sensitivity", "🌍 Emissions", "⚙️ Burn Rate"])

with tab1:
    st.subheader("Daily Cost Comparison at 3 Price Points ($/ton)")
    price_levels = [400, 800, 1200]
    data = []
    for fuel, props in fuel_data.items():
        eff = props.get("eff", 1.0)
        lhv = props["LHV"]
        for price in price_levels:
            burn = energy_MJ_day / (lhv * 1e3 * eff)
            data.append({"Fuel": fuel, "Price ($/ton)": f"${price}", "Daily Cost ($)": burn * price})

    df = pd.DataFrame(data)
    fig = go.Figure()
    for price in price_levels:
        subset = df[df["Price ($/ton)"] == f"${price}"]
        fig.add_trace(go.Bar(x=subset["Fuel"], y=subset["Daily Cost ($)"], name=f"${price}/ton"))

    fig.update_layout(
        barmode="group",
        title="Daily Cost by Fuel at Different Price Points",
        xaxis_title="Fuel",
        yaxis_title="Daily Cost ($)",
        height=420,
        width=720,
        template="plotly_white",
        legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center", font=dict(size=10))
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    emissions = {fuel: energy_MJ_day * props["CI"] / 1e6 for fuel, props in fuel_data.items()}
    fig2 = go.Figure([go.Bar(x=list(emissions.keys()), y=list(emissions.values()))])
    fig2.update_layout(
        title="CO₂e Emissions per Fuel (tons/day)",
        xaxis_title="Fuel",
        yaxis_title="Emissions (tons/day)",
        height=400,
        width=720,
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    burns = {
        fuel: energy_MJ_day / (props["LHV"] * 1e3 * props.get("eff", 1.0))
        for fuel, props in fuel_data.items()
    }
    fig3 = go.Figure([go.Bar(x=list(burns.keys()), y=list(burns.values()))])
    fig3.update_layout(
        title="Fuel Burn Rate (tons/day)",
        xaxis_title="Fuel",
        yaxis_title="Burn Rate (tons/day)",
        height=400,
        width=720,
        template="plotly_white"
    )
    st.plotly_chart(fig3, use_container_width=True)

from pathlib import Path

module2_code = """
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# -------------------------------
# Ship Specs & Policy Parameters
# -------------------------------
st.markdown("## ⚙️ Module 2: Switch or Pay Strategy (IMO 2028)")
ship_power = st.number_input("Ship Power (MW)", value=60.0, min_value=1.0)
operation_hours = st.number_input("Operation Hours per Day", value=24, min_value=1, max_value=24)
ci_reduction = st.slider("CI Reduction Target (%)", min_value=0, max_value=40, value=4, step=1)
carbon_fee = st.number_input("Carbon Fee ($/ton CO₂)", value=380, step=10)

# -------------------------------
# Fuel Data (CI, LHV, Price, CapEx, Infra)
# -------------------------------
fuel_data = {
    "VLSFO": {"LHV": 42.7, "Price": 650, "CI": 91, "CapEx": 0, "Infra": 0},
    "Green Methanol": {"LHV": 20, "Price": 950, "CI": 10, "CapEx": 10_000_000, "Infra": 5000},
    "Green Ammonia": {"LHV": 18.6, "Price": 1200, "CI": 5, "CapEx": 15_000_000, "Infra": 18000},
    "Green Hydrogen (FC)": {"LHV": 120, "Price": 4500, "CI": 3, "CapEx": 25_000_000, "Infra": 22000, "eff": 0.55},
}

# -------------------------------
# Constants
# -------------------------------
baseline_CI = 93.3
ci_target = baseline_CI * (1 - ci_reduction / 100)
energy_MJ_day = ship_power * 1e3 * operation_hours
discount_rate = 0.08
lifetime_years = 20
days_per_year = 365

# -------------------------------
# Calculation Function
# -------------------------------
def calculate_fuel_row(name, props):
    eff = props.get("eff", 1.0)
    burn = energy_MJ_day / (props["LHV"] * 1e3 * eff)
    fuel_cost = burn * props["Price"]
    emissions = energy_MJ_day * props["CI"] / 1e6
    excess_CI = max(props["CI"] - ci_target, 0)
    excess_CO2 = excess_CI * energy_MJ_day / 1e6
    fee = excess_CO2 * carbon_fee
    capex_day = (props["CapEx"] * discount_rate) / (1 - (1 + discount_rate) ** (-lifetime_years)) / days_per_year
    total_cost = fuel_cost + fee + capex_day + props["Infra"]
    return {
        "Fuel": name,
        "Burn Rate (t/day)": round(burn, 2),
        "Fuel Cost ($/day)": round(fuel_cost, 0),
        "Carbon Fee ($/day)": round(fee, 0),
        "CapEx/day": round(capex_day, 0),
        "Infra/day": round(props["Infra"], 0),
        "Total Cost ($/day)": round(total_cost, 0),
    }

# -------------------------------
# Calculate & Display
# -------------------------------
results = [calculate_fuel_row(name, props) for name, props in fuel_data.items()]
df = pd.DataFrame(results)

st.markdown(f"### 📊 CI Target: {ci_target:.2f} gCO₂e/MJ")
st.dataframe(df.set_index("Fuel"))

fig = go.Figure()
fig.add_trace(go.Bar(x=df["Fuel"], y=df["Total Cost ($/day)"], name="Total Daily Cost"))
fig.update_layout(title="Total Daily Operating Cost per Fuel", yaxis_title="$/day", template="plotly_white", height=400)
st.plotly_chart(fig, use_container_width=True)
"""

file_path = Path("/mnt/data/module2_switch_or_pay.py")
file_path.write_text(module2_code)
file_path.name

