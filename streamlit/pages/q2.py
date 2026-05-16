import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from scipy.spatial import distance
from common import final  


st.title("🚛 Emergency Logistics Rerouting")
st.markdown("""
This map identifies stores in the **Danger Zone** (East of -81.5 Longitude) with high **Priority Scores**. 
These stores are automatically rerouted from coastal hubs to safe inland hubs (Atlanta/Charlotte).
""")

dc_data = {
    'DC_ID': ['DC1', 'DC3', 'DC4'], 
    'DC_Name': ['Atlanta Hub', 'Charlotte Hub', 'Jacksonville Hub'], 
    'Latitude_dc': [33.7, 35.2, 30.3],
    'Longitude_dc': [-84.3, -80.8, -81.6]
}
dc_df = pd.DataFrame(dc_data)

st.sidebar.header("Reroute Parameters")
priority_val = st.sidebar.slider("Priority Percentile Threshold", 0.50, 0.99, 0.85)
priority_threshold = final['Priority_Score'].quantile(priority_val)

coastal_risk_boundary = st.sidebar.number_input("Coastal Boundary (Longitude)", value=-81.5)

rerouted_count = 0
standard_count = 0

for idx, store in final.iterrows():
    is_high_priority = store['Priority_Score'] > priority_threshold
    is_in_danger_zone = store['Longitude_store'] > coastal_risk_boundary

    if is_high_priority and is_in_danger_zone:
        rerouted_count += 1
    else:
        standard_count += 1

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Stores Rerouted", rerouted_count)

with col2:
    st.metric("Standard Lanes", standard_count)

with col3:
    st.metric("Priority Threshold", f"{priority_threshold:.2f}")

m_reroute = folium.Map(location=[32.0, -82.5], zoom_start=6, tiles='CartoDB positron')

safe_dcs = dc_df[dc_df['DC_Name'].str.contains('Atlanta|Charlotte')] 

for idx, store in final.iterrows():
    store_coords = [store['Latitude_store'], store['Longitude_store']]
    primary_dc_coords = [store['Latitude_dc'], store['Longitude_dc']]
    
    is_high_priority = store['Priority_Score'] > priority_threshold
    is_in_danger_zone = store['Longitude_store'] > coastal_risk_boundary

    if is_high_priority and is_in_danger_zone:
        distances = []
        for i, dc in safe_dcs.iterrows():
            dist = distance.euclidean(store_coords, [dc['Latitude_dc'], dc['Longitude_dc']])
            distances.append((dist, dc))
        
        best_dc = min(distances, key=lambda x: x[0])[1]
        emergency_coords = [best_dc['Latitude_dc'], best_dc['Longitude_dc']]
        
        folium.PolyLine(
            locations=[store_coords, emergency_coords],
            color='#004b87', weight=4, opacity=0.8, dash_array='10',
            tooltip=f"REROUTE: {store['City_store']} to {best_dc['DC_Name']}"
        ).add_to(m_reroute)
        
        folium.CircleMarker(
            location=store_coords, radius=8, color='red', fill=True, fill_color='red',
            popup=f"CRITICAL: {store['City_store']} -> {best_dc['DC_Name']}"
        ).add_to(m_reroute)
    else:
        folium.PolyLine(
            locations=[store_coords, primary_dc_coords],
            color='gray', weight=1, opacity=0.3
        ).add_to(m_reroute)
        
        dot_color = 'orange' if is_high_priority else 'green'
        folium.CircleMarker(
            location=store_coords, radius=4, color=dot_color, fill=True,
            popup=f"{store['City_store']}: Standard Lane"
        ).add_to(m_reroute)

for _, dc in dc_df.iterrows():
    folium.Marker(
        location=[dc['Latitude_dc'], dc['Longitude_dc']],
        icon=folium.Icon(color='black', icon='star'),
        tooltip=f"HUB: {dc['DC_Name']}"
    ).add_to(m_reroute)

st_folium(m_reroute, width=1200, height=600)

st.info("""
**Legend:**
* ⭐ **Black Star:** Distribution Hub
* 🔴 **Large Red Dot:** Rerouted Critical Store
* 🟠 **Orange Dot:** High Priority (Inland - No Reroute)
* 🟢 **Small Green Dot:** Normal Operation
""")

with st.expander("View rerouting data"):
    st.dataframe(final, use_container_width=True)