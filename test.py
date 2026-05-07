import streamlit as st
import pandas as pd
from datetime import datetime
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- FILES ----------
csv_file = "incident_reports.csv"
pdf_file = "latest_incident_report.pdf"

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Incident Report System",
    page_icon="📋",
    layout="centered"
)

# ---------- STYLE ----------
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

# ---------- PDF FUNCTION ----------
def create_pdf(data):
    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Incident Report", styles["Title"]))
    content.append(Spacer(1, 12))

    for key, value in data.items():
        line = f"<b>{key}:</b> {value}"
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 8))

    doc.build(content)

# ---------- FORM ----------
with st.form("incident_form"):

    st.markdown("### 1. Basic Information")

    client_name = st.text_input("Client Name")
    incident_date = st.date_input("Date of Incident")
    staff_reporting = st.text_input("Staff Reporting")
    witness = st.text_input("Witness (if applicable)")

    st.markdown("### 2. Type of Report")

    incident_type = st.selectbox(
        "Incident Type",
        ["Aggression", "Property Destruction", "Self Injury", "Elopement", "Verbal Protest", "Other"]
    )

    other_incident = ""
    if incident_type == "Other":
        other_incident = st.text_input("Describe Other Incident Type")

    location = st.text_input("Location")

    medical_involved = st.selectbox("Was Medical Involved?", ["No", "Yes"])

    incident_description = st.text_area("Incident Description")

    st.markdown("### 3. Actions / Notes")

    witness_statement = st.text_area("Witness Statement")

    submitted = st.form_submit_button("Submit Report")

# ---------- SUBMIT ----------
if submitted:

    report = {
        "Client Name": client_name,
        "Incident Date": str(incident_date),
        "Staff Reporting": staff_reporting,
        "Witness": witness,
        "Incident Type": incident_type,
        "Other Incident Detail": other_incident,
        "Location": location,
        "Medical Involved": medical_involved,
        "Description": incident_description,
        "Witness Statement": witness_statement,
        "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    df = pd.DataFrame([report])

    # Save CSV
    if os.path.exists(csv_file):
        old = pd.read_csv(csv_file)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(csv_file, index=False)

    # Create PDF
    create_pdf(report)

    st.success("✅ Incident Report Submitted Successfully!")

    # Download PDF
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📄 Download PDF Report",
            data=f,
            file_name=f"incident_report_{client_name}.pdf",
            mime="application/pdf"
        )

# ---------- VIEW REPORTS ----------
st.divider()
st.subheader("Submitted Reports")

if os.path.exists(csv_file):
    st.dataframe(pd.read_csv(csv_file), use_container_width=True)
else:
    st.info("No reports submitted yet.")