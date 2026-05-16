import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from common import final


st.title("Network Depletion vs. Storm Proximity")
st.markdown("""
This page visualizes how inventory levels and sales volume correlate with the 
approach of a storm.
""")

timeline = final.groupby('Date').agg({
    'Inventory_On_Hand': 'sum',
    'Units_Sold': 'sum',
    'Storm_Proximity': 'mean'
}).reset_index()
timeline['Date'] = pd.to_datetime(timeline['Date'])

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Inventory & Demand Timeline")
   
    sns.set_style("white")
    fig, ax1 = plt.subplots(figsize=(14, 7))

    ax1.fill_between(timeline['Date'], timeline['Inventory_On_Hand'], color='green', alpha=0.2, label='Total Network Inventory')
    ax1.plot(timeline['Date'], timeline['Inventory_On_Hand'], color='green', linewidth=3)
    ax1.bar(timeline['Date'], timeline['Units_Sold'], color='#FF8C00', alpha=0.5, label='Units Sold (Demand)')
    ax1.set_ylabel('Unit Volume', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(timeline['Date'], timeline['Storm_Proximity'], color='#CC0000', linestyle='--', linewidth=2, marker='o', label='Storm proximity (Miles)')
    ax2.set_ylabel('Storm proximity (Miles)', color='#CC0000', fontsize=12, fontweight='bold')
    ax2.invert_yaxis() 
    ax2.tick_params(axis='y', labelcolor='#CC0000', labelsize=10)


    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fontsize=10)

    sns.despine(right=False)
    plt.tight_layout()
    
    st.pyplot(fig)

def highlight_inversion(row):
    """Highlights rows where Units Sold > Inventory (The Inversion Point)"""
    color = 'background-color: rgba(255, 0, 0, 0.2)' if row['Units_Sold'] > row['Inventory_On_Hand'] else ''
    return [color] * len(row)

def highlight_proximity(val):
    """Highlights storm proximity under 100 miles in red bold text"""
    color = 'red' if val < 100 else 'black'
    weight = 'bold' if val < 100 else 'normal'
    return f'color: {color}; font-weight: {weight}'

with col2:
    st.subheader("Pre-landfall metrics")
   
    peak_demand = timeline['Units_Sold'].max()
    baseline_demand = timeline['Units_Sold'].iloc[0]
    surge_multiplier = peak_demand / baseline_demand if baseline_demand > 0 else 0
   
    total_start_inv = timeline['Inventory_On_Hand'].iloc[0]
    total_end_inv = timeline['Inventory_On_Hand'].iloc[-1]
    depletion_pct = ((total_start_inv - total_end_inv) / total_start_inv) * 100
   
    current_inv = timeline['Inventory_On_Hand'].iloc[-1]
    current_demand = timeline['Units_Sold'].iloc[-1]
    days_to_zero = current_inv / current_demand if current_demand > 0 else 0

    st.metric(
        label="Demand Surge Intensity", 
        value=f"{surge_multiplier:.1f}x", 
        delta="Above Baseline",
        delta_color="inverse",
        help="How many times higher demand is compared to standard daily baseline."
    )
   
    st.metric(
        label="Network Depletion", 
        value=f"{abs(depletion_pct):.1f}%", 
        delta=f"{int(total_end_inv):,} units left",
        delta_color="inverse",
        help="Percentage of total regional inventory already gone because of the storm surge"
    )
   
st.divider()
st.subheader("Timeline Data Source: Critical Events Highlighted")
st.info("🔴 **Red Rows** indicate the 'Inversion point' where Demand exceeded On-Hand Inventory.")

styled_timeline = (timeline.style
    .apply(highlight_inversion, axis=1)
    .applymap(highlight_proximity, subset=['Storm_Proximity']) 
    .format({
        'Inventory_On_Hand': "{:,.0f}", 
        'Units_Sold': "{:,.0f}", 
        'Storm_Proximity': "{:.1f} mi"
    })
)

st.dataframe(styled_timeline, use_container_width=True)
