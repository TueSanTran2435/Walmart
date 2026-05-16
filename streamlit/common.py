import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder


def get_storm():
    return pd.read_csv('https://storage.googleapis.com/data-vis-open-access-p2/walmart/storm_data.csv')

def get_distribution_centers():
    return pd.read_csv('https://storage.googleapis.com/data-vis-open-access-p2/walmart/distribution_centers.csv')

def get_store_network_lanes():
    return pd.read_csv('https://storage.googleapis.com/data-vis-open-access-p2/walmart/store_network_lanes.csv')

storm = get_storm()
distribution_centers = get_distribution_centers()
store_network_lanes = get_store_network_lanes()

storm.drop_duplicates(inplace=True)
distribution_centers.drop_duplicates(inplace=True)
store_network_lanes.drop_duplicates(inplace=True)

storm['Date'] = pd.to_datetime(storm['Date'])
storm['Store_ID'] = storm['Store_ID'].astype(str)
store_network_lanes['Store_ID'] = store_network_lanes['Store_ID'].astype(str)
store_network_lanes['Primary_DC_Link'] = store_network_lanes['Primary_DC_Link'].astype(str)
distribution_centers['DC_ID'] = distribution_centers['DC_ID'].astype(str)

merged1 = pd.merge(storm, store_network_lanes, on='Store_ID', how='inner') 
final = pd.merge(merged1, distribution_centers, left_on='Primary_DC_Link', right_on='DC_ID', how='inner', suffixes=('_store', '_dc'))

final['Demand_Spike_Ratio'] = final['Units_Sold'] / final['Avg_Daily_Sales'].replace(0, np.nan)
final['Storm_Urgency'] = 1 / (final['Storm_Proximity'] + 1)
final['Inventory_Coverage_Days'] = final['Inventory_On_Hand'] / final['Avg_Daily_Sales']
final['Lead_Time_Risk'] = final['Lead_Time_Days'] - final['Inventory_Coverage_Days']
final['Priority_Score'] = (final['Demand_Spike_Ratio'] * final['Storm_Urgency'] * final['Lead_Time_Risk'].clip(lower=0))

def render_aggrid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filterable=True, selectable=True, filter="agTextColumnFilter") 
    grid_options = gb.build()
    return AgGrid(df, gridOptions=grid_options, height=400)
