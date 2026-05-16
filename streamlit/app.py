import streamlit as st

# Cheat sheet: https://docs.streamlit.io/develop/quick-reference/cheat-sheet
# Streamlit emojis: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app
# Emoji finder: https://emojifinder.com/

st.set_page_config(page_title="", layout="wide")

q0 = st.Page("pages/q0.py", title="Welcome")
q1 = st.Page("pages/q1.py", title="Network Depletion vs Storm Proximity")
q3 = st.Page("pages/q3.py", title="Product Demand Concentration")
q4 = st.Page("pages/q4.py", title="Distribution Center Pressure")
q2 = st.Page("pages/q2.py", title="Emergency Rerouting Map")

pg = st.navigation({"Exploration": [q0, q1, q3, q4, q2]})


pg.run()
