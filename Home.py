import streamlit as st
import os


st.set_page_config(page_title="Hoyalytics Bond Yield Predictor", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0A1D3C;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("Welcome to the Hoyalytics Bond Yield Predictor")
    
    
    image_path = os.path.join("images", "HOYA PIC.jpg")  

    if os.path.exists(image_path):
        st.image(image_path, width=250) 
    else:
        st.warning("Logo image not found. Please ensure the image exists at: " + image_path)
    
    st.write("Explore our bond yield prediction tool. Click the button below to continue to the dashboard.")

    # Button to navigate to the Dashboard page
    if st.button("Continue to Dashboard"):
        st.switch_page("pages/graph.py")
