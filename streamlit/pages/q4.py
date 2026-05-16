import streamlit as st
import altair as alt
import numpy as np
from common import final

st.title("Distribution Center Pressure")
st.subheader("Identify which DCs support the highest-risk demand zones")

st.markdown("This page ranks distribution centers by average priority score.")

st.divider()

data = final.copy()

if "Demand_Spike_Ratio" not in data.columns:
    data["Demand_Spike_Ratio"] = data["Units_Sold"] / data["Avg_Daily_Sales"].replace(0, np.nan)

if "Inventory_Coverage_Days" not in data.columns:
    data["Inventory_Coverage_Days"] = data["Inventory_On_Hand"] / data["Avg_Daily_Sales"].replace(0, np.nan)

if "Lead_Time_Risk" not in data.columns:
    data["Lead_Time_Risk"] = data["Lead_Time_Days"] - data["Inventory_Coverage_Days"]

if "Storm_Urgency" not in data.columns:
    data["Storm_Urgency"] = 1 / (data["Storm_Proximity"] + 1)

if "Priority_Score" not in data.columns:
    data["Priority_Score"] = (
        data["Demand_Spike_Ratio"]
        * data["Storm_Urgency"]
        * data["Lead_Time_Risk"].clip(lower=0)
    )

dc_priority = (
    data.groupby(["DC_ID", "DC_Name"], as_index=False)
    .agg({
        "Priority_Score": "mean",
        "Store_ID": "nunique",
        "Units_Sold": "sum",
        "Inventory_On_Hand": "sum"
    })
)

dc_priority = dc_priority.sort_values("Priority_Score", ascending=False)

st.sidebar.header("Filters")

top_n = st.sidebar.slider(
    "DCs shown",
    min_value=1,
    max_value=len(dc_priority),
    value=len(dc_priority)
)

dc_filtered = dc_priority.head(top_n).copy()
top_dc = dc_filtered.nlargest(1, "Priority_Score")["DC_Name"].iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    top_dc = dc_filtered.nlargest(1, "Priority_Score")["DC_Name"].iloc[0]
    st.metric("Highest Pressure DC", top_dc)

with col2:
    st.metric("Avg Priority Score", f"{dc_filtered['Priority_Score'].max():.2f}")

with col3:
    st.metric("DCs Shown", len(dc_filtered))

st.divider()

dc_chart = alt.Chart(dc_filtered).mark_bar().encode(
    x=alt.X(
        "Priority_Score:Q",
        title="Average Priority Score"
    ),
    y=alt.Y(
        "DC_Name:N",
        sort="-x",
        title="Distribution Center"
    ),
    color=alt.condition(
        alt.datum.DC_Name == top_dc,
        alt.value("#b22222"),
        alt.value("lightgray")
    ),
    tooltip=[
        alt.Tooltip("DC_ID:N", title="DC ID"),
        alt.Tooltip("DC_Name:N", title="DC Name"),
        alt.Tooltip("Priority_Score:Q", title="Avg Priority", format=".2f"),
        alt.Tooltip("Store_ID:Q", title="Stores Supported"),
        alt.Tooltip("Units_Sold:Q", title="Units Sold", format=",.0f"),
        alt.Tooltip("Inventory_On_Hand:Q", title="Inventory", format=",.0f")
    ]
).properties(
    width=700,
    height=350,
    title="One Distribution Center Faces the Highest Supply Chain Pressure"
)
st.altair_chart(dc_chart, use_container_width=True)

st.success(
    f"{top_dc} has the highest average priority score, meaning it supports the most urgent store-product demand zones."
)

with st.expander("View DC summary data"):
    display_table = dc_priority.copy()

    display_table["Priority_Score"] = display_table["Priority_Score"].round(2)

    display_table = display_table.rename(columns={
        "DC_ID": "DC ID",
        "DC_Name": "Distribution Center",
        "Priority_Score": "Average Priority Score",
        "Store_ID": "Stores Supported",
        "Units_Sold": "Units Sold",
        "Inventory_On_Hand": "Inventory On Hand"
    })

    st.dataframe(display_table, use_container_width=True)

with st.expander("View full row-level data"):
    st.dataframe(data, use_container_width=True)