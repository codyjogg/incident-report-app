import streamlit as st
import pandas as pd
from datetime import datetime
import os

file_name = "incident_reports.csv"

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Incident Report System",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ======================
# CUSTOM STYLE
# ======================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #1e1e2f, #2b2b45);
    color: white;
}

.main-title {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    margin-bottom: 20px;
    color: white;
}

div[data-testid="stForm"] {
    background-color: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📋 Incident Report System</div>', unsafe_allow_html=True)

# ======================
# DASHBOARD SUMMARY
# ======================
st.markdown("## 📊 Dashboard Summary")

col1, col2, col3 = st.columns(3)

if os.path.exists(file_name):
    df = pd.read_csv(file_name)

    total_reports = len(df)
    high_risk = len(df[df["Severity"] == "Severe"]) if "Severity" in df.columns else 0
    today_reports = len(df[df["Submitted At"].astype(str).str.contains(str(datetime.now().date()))])

    col1.metric("Total Reports", total_reports)
    col2.metric("High Risk", high_risk)
    col3.metric("Today", today_reports)

else:
    col1.metric("Total Reports", 0)
    col2.metric("High Risk", 0)
    col3.metric("Today", 0)

st.divider()

# ======================
# FORM
# ======================
with st.form("incident_form"):

    st.markdown("### 🧾 Basic Information")
    client_name = st.text_input("Client Name")
    incident_date = st.date_input("Date of Incident")
    staff_reporting = st.text_input("Staff Reporting")
    witness = st.text_input("Witness (if applicable)")

    st.divider()

    st.markdown("### 🚨 Incident Details")
    medical_emergency = st.selectbox(
        "Medical Emergency",
        ["None", "Seizure", "Allergic Reaction", "Difficulty Breathing", "Other"]
    )

    medical_other = ""
    if medical_emergency == "Other":
        medical_other = st.text_input("Specify Medical Emergency")

    client_injury = st.selectbox("Client Injury Severity", ["None", "Minor", "Moderate", "Severe"])
    client_injury_desc = st.text_input("Client Injury Description")

    staff_injury = st.selectbox("Staff Injury Severity", ["None", "Minor", "Moderate", "Severe"])
    staff_injury_desc = st.text_input("Staff Injury Description")

    property_damage = st.selectbox("Property Damage", ["No", "Yes"])
    property_damage_desc = ""

    if property_damage == "Yes":
        property_damage_desc = st.text_input("Describe Property Damage")

    other_report = st.text_input("Other Notes")

    st.divider()

    with st.expander("🩺 Body Check (Expand)"):
        body_locations = st.multiselect(
            "Location of Injuries",
            ["Head", "Face", "Neck", "Shoulders", "Arms", "Hands", "Chest", "Back", "Abdomen", "Hips", "Legs", "Feet", "Other"]
        )

        body_other = ""
        if "Other" in body_locations:
            body_other = st.text_input("Specify Other Location")

        injury_types = st.multiselect(
            "Injury Types",
            ["Bruising", "Scratches", "Cuts", "Swelling", "Redness", "Abrasions", "Bites", "Broken Skin", "Other"]
        )

        injury_other = ""
        if "Other" in injury_types:
            injury_other = st.text_input("Specify Other Injury Type")

        severity = st.selectbox(
            "Severity of Injury",
            ["Minor", "Moderate", "Severe", "Requires Medical Attention"]
        )

    st.divider()

    with st.expander("⚠️ Abuse / Actions / Signatures"):
        abuse = st.selectbox("Was Abuse Suspected?", ["No", "Yes"])
        abuse_signs = st.text_area("Signs Observed")

        actions_taken = st.multiselect(
            "Actions Taken",
            ["Cleaned wound", "Applied bandage", "Applied ice pack", "Called first responders", "Other"]
        )

        actions_other = ""
        if "Other" in actions_taken:
            actions_other = st.text_input("Specify Other Action")

        supervisor_notified = st.selectbox("Supervisor Notified", ["No", "Yes"])
        cps_notified = st.selectbox("CPS Notified", ["No", "Yes"])
        notif_time = st.text_input("Notification Time")

        guardian_notified = st.selectbox("Guardian Notified", ["No", "Yes"])
        guardian_time = st.text_input("Guardian Notification Time")

        witness_statement = st.text_area("Witness Statement")

        prepared_by = st.text_input("Prepared By")
        report_date = st.date_input("Report Date")
        reviewed_by = st.text_input("Reviewed By")
        supervisor_signature = st.text_input("Supervisor Signature")

    submitted = st.form_submit_button("Submit Report")

# ======================
# SAVE DATA
# ======================
if submitted:

    data = {
        "Client Name": client_name,
        "Incident Date": incident_date,
        "Staff Reporting": staff_reporting,
        "Witness": witness,

        "Medical Emergency": medical_emergency,
        "Medical Other": medical_other,

        "Client Injury": client_injury,
        "Client Injury Desc": client_injury_desc,

        "Staff Injury": staff_injury,
        "Staff Injury Desc": staff_injury_desc,

        "Property Damage": property_damage,
        "Property Damage Desc": property_damage_desc,
        "Other Report": other_report,

        "Body Locations": ", ".join(body_locations),
        "Body Other": body_other,

        "Injury Types": ", ".join(injury_types),
        "Injury Other": injury_other,
        "Severity": severity,

        "Abuse Suspected": abuse,
        "Abuse Signs": abuse_signs,

        "Actions Taken": ", ".join(actions_taken),
        "Actions Other": actions_other,

        "Supervisor Notified": supervisor_notified,
        "CPS Notified": cps_notified,
        "Notification Time": notif_time,

        "Guardian Notified": guardian_notified,
        "Guardian Time": guardian_time,

        "Witness Statement": witness_statement,

        "Prepared By": prepared_by,
        "Report Date": report_date,
        "Reviewed By": reviewed_by,
        "Supervisor Signature": supervisor_signature,

        "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    df = pd.DataFrame([data])

    if os.path.exists(file_name):
        existing = pd.read_csv(file_name)
        df = pd.concat([existing, df], ignore_index=True)

    df.to_csv(file_name, index=False)

    st.success("✅ Incident Report Submitted Successfully!")

    # Visual feedback
    if severity == "Severe":
        st.error("🔴 HIGH PRIORITY INCIDENT")
    elif severity == "Moderate":
        st.warning("🟠 MEDIUM PRIORITY INCIDENT")
    else:
        st.success("🟢 LOW PRIORITY INCIDENT")

# ======================
# VIEW REPORTS
# ======================
st.divider()
st.subheader("📁 Submitted Reports")

if os.path.exists(file_name):
    st.dataframe(
        pd.read_csv(file_name),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No reports submitted yet.")