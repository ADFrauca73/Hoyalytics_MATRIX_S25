import streamlit as st
import pandas as pd

st.set_page_config(page_title="Select Variables", layout="wide", initial_sidebar_state="collapsed")

st.markdown("<style>[data-testid='stSidebarNav']{display:none;}</style>", unsafe_allow_html=True)

# ─── Custom Styling ────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #000000 0%, #072f5f 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.page-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
}
.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: #cbf0ff;
}
.stButton > button {
    background: linear-gradient(90deg, #3895d3, #58cced) !important;
    color: white !important;
    font-weight: 600;
    padding: 0.75rem 2rem;
    border: none !important;
    border-radius: 6px !important;
}
.stButton > button:hover {
    box-shadow: 0 0 10px #58cced, 0 0 20px #58cced;
}
</style>
""", unsafe_allow_html=True)

# ─── Initialize Session State ─────────────────────────────
if "selected_vars" not in st.session_state:
    st.session_state["selected_vars"] = []
if "selected_tariffs" not in st.session_state:
    st.session_state["selected_tariffs"] = []
if "filtered_df" not in st.session_state:
    st.session_state["filtered_df"] = None

# ─── Hardcoded Descriptive Tariff Mapping ─────────────────
label_mapping = {
    "Chapter 39 – Plastics and articles thereof": "start_tariff_39",
    "Chapter 40 – Rubber and articles thereof": "start_tariff_40",
    "Chapter 72 – Iron and steel": "start_tariff_72",
    "Chapter 73 – Articles of iron or steel": "start_tariff_73",
    "Chapter 74 – Copper and articles thereof": "start_tariff_74",
    "Chapter 75 – Nickel and articles thereof": "start_tariff_75",
    "Chapter 76 – Aluminum and articles thereof": "start_tariff_76",
    "Chapter 78 – Lead and articles thereof": "start_tariff_78",
    "Chapter 79 – Zinc and articles thereof": "start_tariff_79",
    "Chapter 80 – Tin and articles thereof": "start_tariff_80",
    "Chapter 81 – Other base metals; cermets; articles thereof": "start_tariff_81",
    "Chapter 82 – Tools, implements, cutlery, spoons and forks, of base metal": "start_tariff_82",
    "Chapter 83 – Miscellaneous articles of base metal": "start_tariff_83",
    "Chapter 84 – Nuclear reactors, boilers, machinery and mechanical appliances": "start_tariff_84",
    "Chapter 85 – Electrical machinery and equipment; sound recorders and reproducers, etc.": "start_tariff_85",
    "Chapter 86 – Railway or tramway locomotives, rolling-stock, and parts": "start_tariff_86",
    "Chapter 87 – Vehicles other than railway or tramway rolling-stock": "start_tariff_87",
    "Chapter 88 – Aircraft, spacecraft, and parts thereof": "start_tariff_88",
    "Chapter 89 – Ships, boats, and floating structures": "start_tariff_89",
    "Chapter 90 – Optical, photographic, cinematographic, measuring, checking, precision, medical instruments": "start_tariff_90",
    "Chapter 96 – Miscellaneous manufactured articles": "start_tariff_96",
    "Chapter 98 – Special classification provisions (e.g., U.S. goods returned, duty exemptions)": "start_tariff_98"
}
column_to_label = {v: k for k, v in label_mapping.items()}

# ─── UI Layout ────────────────────────────────────────────
st.markdown("<div class='page-title'>Select Variables & Tariffs</div>", unsafe_allow_html=True)
left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    st.subheader("Include these:")
    var_opts = ["Consumer Sentiment / VIX", "M1 Supply", "Inflation / FFR"]
    new_var_selection = st.multiselect(
        "Select variables",
        options=var_opts,
        default=st.session_state["selected_vars"]
    )

with right_col:
    st.subheader("Choose tariffs:")
    tariff_options = list(label_mapping.keys())
    selected_labels = [column_to_label.get(col) for col in st.session_state["selected_tariffs"] if col in column_to_label]
    new_tariff_selection = st.multiselect(
        "Select one or more tariff chapters",
        options=tariff_options,
        default=selected_labels
    )
    selected_tariff_columns = [label_mapping[label] for label in new_tariff_selection if label in label_mapping]

# ─── Apply Button ─────────────────────────────────────────
if st.button("Apply Selections", use_container_width=True):
    st.session_state["selected_vars"] = new_var_selection
    st.session_state["selected_tariffs"] = selected_tariff_columns

    if st.session_state["filtered_df"] is None:
        st.warning("No business-day data found. Please run the Dashboard page first.")
    else:
        df = st.session_state["filtered_df"].copy()

        # Step 1: Always preserve the business day
        final_order = ["Business Day"]

        # Step 2: All tariffs (sorted by start_tariff_XX)
        tariff_cols = sorted([col for col in df.columns if col.startswith("start_tariff_")])
        final_order += tariff_cols

        # Step 3: Append selected variables in exact order (if present)
        ordered_variable_cols = [
            ("Inflation / FFR", ["diff_FFR", "diff_CPI"]),
            ("Consumer Sentiment / VIX", ["VIX_close", "diff_CSD"]),
            ("M1 Supply", ["diff_M1_supply"])
        ]

        for ui_label, columns in ordered_variable_cols:
            if ui_label in new_var_selection:
                final_order.extend([col for col in columns if col in df.columns])

        # Step 4: Filter the DataFrame to just the final column order
        df = df[[col for col in final_order if col in df.columns]]

        # Save to session
        st.session_state["filtered_df"] = df
        st.success("Tariffs and variables reordered successfully.")

# ─── Preview ──────────────────────────────────────────────
if st.session_state["filtered_df"] is not None:
    st.dataframe(st.session_state["filtered_df"], use_container_width=True)

# ─── Navigation ───────────────────────────────────────────
c1, _, c2 = st.columns([1, 6, 1])
with c1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/Dashboard.py")
with c2:
    if st.button("Next ➡️"):
        st.switch_page("pages/data2.py")
