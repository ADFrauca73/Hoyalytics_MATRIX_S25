import streamlit as st
import os

st.set_page_config(page_title="Hoyalytics Bond Yield Predictor", layout="wide", initial_sidebar_state="collapsed")

# Logo path
logo_path = "images/logo_placeholder.png"
logo_exists = os.path.exists(logo_path)

# Inject CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        180deg,
        #000000 0%,
        #072f5f 100%
    );
}


/* Adjusted NAVBAR Styling */
.nav-link {
    color: white !important;
    text-decoration: none;
    font-weight: 600;
    font-size: 1.2rem;
    margin: 0 1.5rem;
}
.nav-link:hover {
    color: #58cced;
}


.hero h1 {
    font-size: 6rem;  
}

.hero p {
    font-size: 1.35rem;
}

img {
    max-height: 120px !important; /* ⬅️ Bigger logo */
}
/* CTA Button */
.cta-button {
    background: linear-gradient(90deg, #58cced,#3895d3);
    padding: 0.75rem 4rem;
    border-radius: 8px;  
    color: white !important;  
    font-weight: 600;
    text-decoration: none;
    display: inline-block;
    font-size: 1rem;
    border: none;
}
.cta-button:hover {
    opacity: 0.85;
}
            
    .cta-button-wrapper {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 1rem; /* tighten spacing */
    height: 100%; /* ensures vertical centering */
}

/* Hero Section */
.hero h1 {
    font-size: 3.75rem;
    text-align: center;
    margin: 2rem 0 1rem;
}
.hero p {
    font-size: 1.3rem;
    color: #ccc;
    text-align: center;
    margin-bottom: 2.5rem;
}

/* Dashboard Button */
.stButton > button {
    background: linear-gradient(90deg, #3895d3, #58cced);
    border-radius: 999px;
    color: white !important;
    padding: 0.75rem 2rem;
    font-size: 1.125rem;
    font-weight: 600;
    border: none;
    transition: opacity 0.2s ease;
    display: block;
    margin: 0 auto 3rem;
}
.stButton > button:hover {
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# NAV BAR — Streamlit-native layout
col1, col2, col3 = st.columns([2, 6, 2])

# Left: Logo
with col1:
    if logo_exists:
        st.image(logo_path, width=500)
    else:
        st.warning("Logo missing")

# Center: Navigation links
with col2:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; gap: 2.5rem; padding-left: 2rem;">
            <a class="nav-link" href="graph" target="_self">Dashboard</a>
            <a class="nav-link" href="https://www.hoyalytics.com" target="_blank">Hoyalytics Website</a>
            <a class="nav-link" href="https://www.instagram.com/p/DIehWyPPRkP/?img_index=1" target="_blank">Instagram</a>
            <a class="nav-link" style="opacity: 0.6;">Medium (Coming Soon)</a>
            <a class="nav-link" href="https://github.com/ADFrauca73/MATRIX" target="_blank">GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# Right: CTA Button
with col3:
    st.markdown(
    '<div style="text-align: right;"><a class="cta-button" href="https://www.hoyalytics.com/join" target="_blank">Join Us</a></div>',
        unsafe_allow_html=True
    )

# HERO Section
st.markdown("""
<div class="hero">
  <h1>Predicting Your Digital<br>Bond Yields</h1>
  <p>Our platform offers real‑time bond yield predictions, interactive insights, and a seamless user interface—all from your preferred device.</p>
</div>
""", unsafe_allow_html=True)

# Dashboard Button
if st.button("Continue to Dashboard", key="dashboard_button"):
    st.switch_page("pages/Dashboard.py")