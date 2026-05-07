import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Incident Report System",
    page_icon="📝",
    layout="centered"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

/* Main app background */
.stApp {
    background: linear-gradient(to bottom right, #1e1e2f, #2b2b45);
    color: white;
}

/* Title styling */
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 20px;
}

/* Form container */
div[data-testid="stForm"] {
    background-color: rgba(255,255,255,0.08);
    padding: 30px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
}

/* Input boxes */
.stTextInput input,
.stTextArea textarea {
    border-radius: 10px;
}

/* Submit button */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    background-color: #4CAF50;
    color: white;
}

/* Success message */
.stSuccess {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.markdown(
    '<div class="main-title">📝 Incident Report System</div>',
    unsafe_allow_html=True
)

# ---------- FORM ----------
with st.form("incident_form"):

    client_name = st.text_input("Client Name")

    incident_type = st.selectbox(
        "Incident Type",
        [
            "Aggression",
            "Property Destruction",
            "Self Injury",
            "Elopement",
            "Verbal Protest",
            "Other"
        ]
    )

    location = st.text_input("Location")

    incident_description = st.text_area(
        "Incident Description",
        height=200
    )

    submitted = st.form_submit_button("Submit Report")

# ---------- SAVE DATA ----------
if submitted:

    data = {
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Client Name": [client_name],
        "Incident Type": [incident_type],
        "Location": [location],
        "Description": [incident_description]
    }

    df = pd.DataFrame(data)

    file_name = "incident_reports.csv"

    if os.path.exists(file_name):
        existing_df = pd.read_csv(file_name)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_csv(file_name, index=False)
    else:
        df.to_csv(file_name, index=False)

    st.success("✅ Incident Report Submitted Successfully!")

# ---------- VIEW REPORTS ----------
st.divider()

st.subheader("Submitted Reports")

file_name = "incident_reports.csv"

if os.path.exists(file_name):
    reports_df = pd.read_csv(file_name)
    st.dataframe(reports_df, use_container_width=True)
else:
    st.info("No reports submitted yet.")