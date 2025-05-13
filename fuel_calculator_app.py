import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ------------------------
# Fuel Properties
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
# Setup
# ------------------------
st.set_page_config(page_title="Marine Fuel Tool", layout="wide")
st.sidebar.header("🛠️ Ship Specs")
ship_power = st.sidebar.number_input("Ship Power (MW)", 1.0, 100.0, 60.0)
operation_hours = st.sidebar.number_input("Hours per Day", 1, 24, 24)
energy_MJ_day = ship_power * 1e3 * operation_hours

# ------------------------
# Tabs
# ------------------------
tab1, tab2 = st.tabs(["📊 Module 1: Fuel Calculator", "💥 Module 2: Switch or Pay"])

# ------------------------
# Module 1
# ------------------------
with tab1:
    st.header("📊 Fuel Cost & Emissions Calculator")
    selected_fuel = st.selectbox("Select Fuel", list(fuel_data.keys()))
    props = fuel_data[selected_fuel]
    eff = props.get("eff", 1.0)

    burn = energy_MJ_day / (props["LHV"] * 1e3 * eff)
    cost = burn * props["Price"]
    emissions = energy_MJ_day * props["CI"] / 1e6

    st.metric("Burn Rate (t/day)", f"{burn:.2f}")
    st.metric("Fuel Cost ($/day)", f"${cost:,.0f}")
    st.metric("CO₂e (tons/day)", f"{emissions:.2f}")

    tab1a, tab1b, tab1c = st.tabs(["💸 Cost Sensitivity", "🌍 Emissions", "⚙️ Burn Rate"])

    with tab1a:
        prices = np.linspace(200, 1200, 6)
        fig = go.Figure()
        for f in fuel_data:
            LHV = fuel_data[f]["LHV"]
            eff = fuel_data[f].get("eff", 1.0)
            b = energy_MJ_day / (LHV * 1e3 * eff)
            fig.add_trace(go.Scatter(x=prices, y=b * prices, mode='lines', name=f))
        fig.update_layout(title="Daily Cost vs Fuel Price", xaxis_title="$/ton", yaxis_title="Total Cost ($)", height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with tab1b:
        em = {f: energy_MJ_day * fuel_data[f]["CI"] / 1e6 for f in fuel_data}
        fig2 = go.Figure([go.Bar(x=list(em.keys()), y=list(em.values()))])
        fig2.update_layout(title="CO₂e Emissions by Fuel", yaxis_title="tons/day", height=400, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

    with tab1c:
        br = {f: energy_MJ_day / (fuel_data[f]["LHV"] * 1e3 * fuel_data[f].get("eff", 1.0)) for f in fuel_data}
        fig3 = go.Figure([go.Bar(x=list(br.keys()), y=list(br.values()))])
        fig3.update_layout(title="Burn Rate by Fuel", yaxis_title="tons/day", height=400, template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)

# ------------------------
# Module 2
# ------------------------
with tab2:
    st.header("💥 Switch or Pay (IMO 2028)")
    ci_reduction = st.slider("CI Reduction (%)", 0, 40, 4)
    carbon_fee = st.number_input("Carbon Fee ($/ton CO₂)", value=380)
    ci_target = 93.3 * (1 - ci_reduction / 100)
    r, t, y = 0.08, 20, 365

    def row(name, props):
        eff = props.get("eff", 1.0)
        burn = energy_MJ_day / (props["LHV"] * 1e3 * eff)
        fuel_cost = burn * props["Price"]
        ci = props["CI"]
        excess = max(ci - ci_target, 0)
        fee = excess * energy_MJ_day / 1e6 * carbon_fee
        capex = props.get("CapEx", 0)
        infra = props.get("Infra", 0)
        capex_day = (capex * r) / (1 - (1 + r) ** -t) / y
        total = fuel_cost + fee + capex_day + infra
        return {
            "Fuel": name, "Burn Rate": round(burn, 2),
            "Fuel Cost": round(fuel_cost), "Fee": round(fee),
            "CapEx/day": round(capex_day), "Infra/day": infra,
            "Total Cost": round(total)
        }

    df = pd.DataFrame([row(f, p) for f, p in fuel_data.items()])
    st.metric("CI Limit", f"{ci_target:.2f} gCO₂e/MJ")
    st.dataframe(df.set_index("Fuel"))

    fig4 = go.Figure([go.Bar(x=df["Fuel"], y=df["Total Cost"], name="Total Cost")])
    fig4.update_layout(title="Switch vs Pay: Total Daily Cost", yaxis_title="$/day", template="plotly_white", height=400)
    st.plotly_chart(fig4, use_container_width=True)
