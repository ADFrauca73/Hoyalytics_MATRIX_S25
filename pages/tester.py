import streamlit as st

# Set up the page configuration
st.set_page_config(page_title="Tester Page", layout="wide", initial_sidebar_state="collapsed")

# Hide the sidebar navigation
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Page title
st.title("Tester Page")

# Check if required session state data exists
if "filtered_df" not in st.session_state:
    st.error("No data found. Please complete the previous steps.")
    st.stop()

# Display a placeholder for future content
st.write("This is the Tester page. Add your content here.")

# Navigation buttons
col1, _, col2 = st.columns([1, 6, 1])
with col1:
    if st.button("⬅️ Previous", key="prev_btn"):
        st.switch_page("pages/data3.py")
with col2:
    if st.button("Next ➡️", key="next_btn"):
        st.write("Next page functionality not implemented yet.")
