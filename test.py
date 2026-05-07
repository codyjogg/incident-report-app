import streamlit as st

st.title("Incident Report Form")
st.write("Fill out the form below and click submit to save the report.")

# Inputs
name = st.text_input("What is the name?")
time = st.text_input("What time did the incident take place?")
location = st.text_input("Where did the incident take place?")
event = st.text_area("Please describe the incident")
medical = st.selectbox("Was medical involved?", ["Yes", "No"])
injury = st.text_area("Describe any injury (or type None)")

# Button action
if st.button("Submit Report"):

    report = f"""
--- INCIDENT REPORT ---
Name: {name}
Time: {time}
Location: {location}
Incident: {event}
Medical involved: {medical}
Injury: {injury}
-----------------------
"""

    # Save to file
    with open("incident_report.txt", "a") as file:
        file.write(report + "\n")

    st.success("Report saved successfully!")
    st.write("### Preview")
    st.text(report)