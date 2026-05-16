import streamlit as st
import altair as alt
import numpy as np
from common import final

st.title("Product Demand Concentration")
st.subheader("Top SKUs driving storm demand")

st.markdown("Identify which products drive the majority of excess demand.")

st.divider()

data = final.copy()
if "Demand_Spike_Ratio" not in data.columns:
    data["Demand_Spike_Ratio"] = data["Units_Sold"] / data["Avg_Daily_Sales"].replace(0, np.nan)

if "Units_Above_Baseline" not in data.columns:
    data["Units_Above_Baseline"] = data["Units_Sold"] - data["Avg_Daily_Sales"]
sku_concentration = (
    data.groupby("SKU_Name", as_index=False)
    .agg({
        "Units_Above_Baseline": "sum",
        "Demand_Spike_Ratio": "mean"
    })
)
sku_concentration = sku_concentration[
    sku_concentration["Units_Above_Baseline"] > 0
].copy()

total_excess_demand = sku_concentration["Units_Above_Baseline"].sum()

sku_concentration = sku_concentration.sort_values(
    "Units_Above_Baseline",
    ascending=False
)
sku_concentration["Share_of_Excess_Demand"] = (
    sku_concentration["Units_Above_Baseline"] / total_excess_demand
)
st.sidebar.header("Filters")

top_n = st.sidebar.slider(
    "Products shown",
    min_value=5,
    max_value=min(20, len(sku_concentration)),
    value=10
)
highlight_n = st.sidebar.slider(
    "Highlight top",
    min_value=3,
    max_value=top_n,
    value=5
)
sku_filtered = sku_concentration.head(top_n).copy()
highlight_products = sku_concentration.head(highlight_n)["SKU_Name"].tolist()
top5_share = sku_filtered.head(5)["Share_of_Excess_Demand"].sum()
top10_share = sku_filtered.head(10)["Share_of_Excess_Demand"].sum()
displayed_share = sku_filtered["Share_of_Excess_Demand"].sum()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Top 5 Share", f"{top5_share * 100:.1f}%")

with col2:
    st.metric("Top 10 Share", f"{top10_share * 100:.1f}%")

with col3:
    label = f"Top {top_n} Share" if top_n not in [5, 10] else "Displayed Share"
    st.metric(label, f"{displayed_share * 100:.1f}%") 
st.divider()
product_chart = alt.Chart(sku_filtered).mark_bar().encode(
    x=alt.X(
        "Share_of_Excess_Demand:Q",
        title="Share of Demand",
        axis=alt.Axis(format="%")
    ),
    y=alt.Y(
        "SKU_Name:N",
        sort="-x",
        title="Product"
    ),
    color=alt.condition(
        alt.FieldOneOfPredicate(field="SKU_Name", oneOf=highlight_products),
        alt.value("#b22222"),
        alt.value("lightgray")
    ),
    tooltip=[
        alt.Tooltip("SKU_Name:N", title="Product"),
        alt.Tooltip("Units_Above_Baseline:Q", title="Excess Units", format=",.0f"),
        alt.Tooltip("Share_of_Excess_Demand:Q", title="Share", format=".1%"),
        alt.Tooltip("Demand_Spike_Ratio:Q", title="Spike", format=".2f")
    ]
).properties(
    width=700,
    height=420,
    title="Few Products Drive Most Storm Demand"
)
st.altair_chart(product_chart, use_container_width=True)
st.success(f"Top 5 = {top5_share * 100:.1f}%, Top 10 = {top10_share * 100:.1f}% of demand.")

display_table = sku_concentration.copy()

display_table["Share_of_Excess_Demand"] = (display_table["Share_of_Excess_Demand"] * 100).round(1)

display_table["Demand_Spike_Ratio"] = display_table["Demand_Spike_Ratio"].round(2)

display_table = display_table.rename(columns={
        "SKU_Name": "Product",
        "Units_Above_Baseline": "Excess Units",
        "Demand_Spike_Ratio": "Spike Ratio",
        "Share_of_Excess_Demand": "Share (%)"})

with st.expander("View product summary data"):
    st.dataframe(display_table, use_container_width=True)

with st.expander("View full row-level data"):
    st.dataframe(data, use_container_width=True)