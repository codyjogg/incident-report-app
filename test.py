import streamlit as st
import pandas as pd
from datetime import datetime
import os

file_name = "incident_reports.csv"

# ---------- PAGE SETUP ----------
st.set_page_config(
    page_title="Incident Report System",
    page_icon="📝",
    layout="centered"
)

# ---------- CSS ----------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom right, #1e1e2f, #2b2b45);
    color: white;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 20px;
    color: white;
}

div[data-testid="stForm"] {
    background-color: rgba(255,255,255,0.08);
    padding: 30px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.markdown('<div class="main-title">📝 Incident Report System</div>', unsafe_allow_html=True)

# ---------- INPUTS (OUTSIDE FORM FOR DYNAMIC BEHAVIOR) ----------
client_name = st.text_input("Client Name")

incident_type = st.selectbox(
    "Incident Type",
    ["Aggression", "Property Destruction", "Self Injury", "Elopement", "Verbal Protest", "Other"]
)

# ✅ THIS NOW SHOWS INSTANTLY WHEN "OTHER" IS SELECTED
other_incident_detail = ""
if incident_type == "Other":
    other_incident_detail = st.text_input("Please Describe Incident Type")

location = st.text_input("Location")

medical_involved = st.selectbox("Was Medical Involved?", ["No", "Yes"])

incident_description = st.text_area("Incident Description")

# ---------- SUBMIT BUTTON ----------
submitted = st.button("Submit Report")

# ---------- SAVE DATA ----------
if submitted:

    data = {
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Client Name": [client_name],
        "Incident Type": [incident_type],
        "Other Incident Detail": [other_incident_detail],
        "Location": [location],
        "Medical Involved": [medical_involved],
        "Description": [incident_description]
    }

    df = pd.DataFrame(data)

    if os.path.exists(file_name):
        existing_df = pd.read_csv(file_name)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_csv(file_name, index=False)

    st.success("✅ Incident Report Submitted Successfully!")

# ---------- VIEW REPORTS ----------
st.divider()
st.subheader("Submitted Reports")

if os.path.exists(file_name):
    st.dataframe(pd.read_csv(file_name), use_container_width=True)
else:
    st.info("No reports submitted yet.")