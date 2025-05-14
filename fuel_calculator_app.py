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
# Session & Setup
# ------------------------
MAX_USES = 4
st.set_page_config(page_title="Marine Fuel Tool", layout="wide")

if "module_1_uses" not in st.session_state:
    st.session_state["module_1_uses"] = 0
if "module_2_uses" not in st.session_state:
    st.session_state["module_2_uses"] = 0

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

    if st.session_state["module_1_uses"] >= MAX_USES:
        st.warning("🔒 You've reached the limit for this module (4 free uses).")
        st.markdown("👉 [**Subscribe here**](https://buy.stripe.com/00geXhgI85Yn5uUbII)", unsafe_allow_html=True)
    else:
        if st.button("Run Module 1"):
            selected_fuel = st.selectbox("Select Fuel", list(fuel_data.keys()))
            props = fuel_data[selected_fuel]
            eff = props.get("eff", 1.0)
            burn = energy_MJ_day / (props["LHV"] * 1e3 * eff)
            cost = burn * props["Price"]
            emissions = energy_MJ_day * props["CI"] / 1e6

            st.metric("Burn Rate (t/day)", f"{burn:.2f}")
            st.metric("Fuel Cost ($/day)", f"${cost:,.0f}")
            st.metric("CO₂e (tons/day)", f"{emissions:.2f}")

            prices = np.linspace(200, 1200, 6)
            fig = go.Figure()
            for f in fuel_data:
                LHV = fuel_data[f]["LHV"]
                eff = fuel_data[f].get("eff", 1.0)
                b = energy_MJ_day / (LHV * 1e3 * eff)
                fig.add_trace(go.Scatter(x=prices, y=b * prices, mode='lines', name=f))
            fig.update_layout(title="Daily Cost vs Fuel Price", xaxis_title="$/ton", yaxis_title="Total Cost ($)", height=400)
            st.plotly_chart(fig, use_container_width=True)

            st.session_state["module_1_uses"] += 1

# ------------------------
# Module 2
# ------------------------
with tab2:
    st.header("💥 Switch or Pay (IMO Tier 2 Corrected)")

    if st.session_state["module_2_uses"] >= MAX_USES:
        st.warning("🔒 You've reached the limit for this module (4 free uses).")
        st.markdown("👉 [**Subscribe here**](https://buy.stripe.com/00geXhgI85Yn5uUbII)", unsafe_allow_html=True)
    else:
        if st.button("Run Module 2"):
            ci_reduction = st.slider("CI Reduction Target (%)", 0, 40, 4)
            carbon_fee = st.number_input("Carbon Fee ($/ton CO₂e)", value=380)
            ci_target = 93.3 * (1 - ci_reduction / 100)
            st.metric("📉 Tier 2 CI Limit", f"{ci_target:.2f} gCO₂e/MJ")

            def compute_costs(fuel_name, props):
                LHV = props["LHV"]
                CI = props["CI"]
                eff = props.get("eff", 1.0)
                price = props["Price"]
                capex = props.get("CapEx", 0)
                infra = props.get("Infra", 0)
                burn = energy_MJ_day / (LHV * 1e3 * eff)
                fuel_cost = burn * price
                excess_ci = max(CI - ci_target, 0)
                fee = (excess_ci * energy_MJ_day / 1e6) * carbon_fee
                capex_day = (capex * 0.08) / (1 - (1 + 0.08) ** (-20)) / 365 if capex else 0
                total = fuel_cost + fee + capex_day + infra
                return {
                    "Fuel": fuel_name,
                    "Fuel Cost ($/day)": fuel_cost,
                    "Carbon Fee ($/day)": fee,
                    "CapEx/day ($)": capex_day,
                    "Infra/day ($)": infra,
                    "Total Cost ($/day)": total
                }

            df = pd.DataFrame([compute_costs(f, p) for f, p in fuel_data.items()])
            st.dataframe(
                df.set_index("Fuel").style.format({
                    "Fuel Cost ($/day)": "${:,.0f}",
                    "Carbon Fee ($/day)": "${:,.0f}",
                    "CapEx/day ($)": "${:,.0f}",
                    "Infra/day ($)": "${:,.0f}",
                    "Total Cost ($/day)": "${:,.0f}"
                })
            )

            fig = go.Figure()
            fig.add_trace(go.Bar(x=df["Fuel"], y=df["Fuel Cost ($/day)"], name="Fuel Cost"))
            fig.add_trace(go.Bar(x=df["Fuel"], y=df["Carbon Fee ($/day)"], name="Carbon Fee"))
            fig.add_trace(go.Bar(x=df["Fuel"], y=df["CapEx/day ($)"], name="CapEx"))
            fig.add_trace(go.Bar(x=df["Fuel"], y=df["Infra/day ($)"], name="Infra"))
            fig.update_layout(
                barmode="stack",
                title="💰 Daily Cost Breakdown by Fuel Type",
                xaxis_title="Fuel",
                yaxis_title="Total Cost ($/day)",
                height=460,
                template="plotly_white",
                legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center")
            )
            st.plotly_chart(fig, use_container_width=True)

            st.session_state["module_2_uses"] += 1

# ------------------------
# Footer
# ------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("🄯 This Software was developed by The Carbon Shift, all rights reserved.")
