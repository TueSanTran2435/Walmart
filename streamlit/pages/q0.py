
import streamlit as st


st.title("Storm-Driven Supply Chain Optimization")
st.subheader("Predictive Rerouting & Demand Management System")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛑 The Core Problem")
    st.error("""
    **Reactive vs. Proactive:** Walmart’s current supply chain reacts to storm-driven demand **after** it occurs, leading to:
    * **Stockouts** at high-risk coastal stores.
    * **Choke points** at specific coastal Distribution Centers (DCs).
    * **Lost revenue** during critical peak demand windows.
    """)

with col2:
    st.markdown("### 🎯 Analysis Objectives")
    st.info("""
    * **Pinpoint spikes:** Identify when demand surges relative to storm proximity.
    * **Resource shift:** Recommend how to move supply **before** the inventory depletion happens.
    * **Load balancing:** Redistribute pressure away from overloaded coastal hubs to inland havens.
    """)

st.divider()

st.markdown("### Navigation")
st.write("Quickly access the four key pillars of the analysis:")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(label="Finding #1", value="Timeline")
    if st.button("Go to Network Depletion", use_container_width=True):
        st.switch_page("pages/q1.py")
    st.caption("Correlation between storm distance and inventory levels.")

with c2:
    st.metric(label="Finding #2", value="Overloaded")
    if st.button("Go to DC Analysis", use_container_width=True):
        st.switch_page("pages/q4.py")
    st.caption("Identifying distribution centers under maximum pressure.")

with c3:
    st.metric(label="Finding #3", value="Product mix")
    if st.button("Go to Demand Share", use_container_width=True):
        st.switch_page("pages/q3.py")
    st.caption("Top 10 products driving 95% of excess demand.")

with c4:
    st.metric(label="Solution", value="Rerouting")
    if st.button("Go to Rerouting Model", use_container_width=True):
        st.switch_page("pages/q2.py")
    st.caption("Emergency flex logic from coastal to inland hubs.")

st.divider()

st.markdown("### Key Takeaways")
st.success("""
1. **Excess demand:** 79% of excess demand is driven by just 5 products (Ice, Trash Bags, Propane, etc.).
2. **The 100-Mile Rule:** Units sold spike aggressively once a storm is within 100 miles; inventory must be staged by the 250-mile mark.
3. **Inland flex:** Implementing the 'Emergency Flex' to Atlanta/Charlotte prevents the Coastal Logistics center from doubling its capacity limit.
""")
