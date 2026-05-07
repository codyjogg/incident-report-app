import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

# ── optional deps (graceful fallback) ──────────────────────────────────────
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.units import inch
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ── constants ───────────────────────────────────────────────────────────────
FILE_NAME = "incident_reports.csv"
SEVERITY_ORDER = ["Minor", "Moderate", "Severe", "Requires Medical Attention"]
SEVERITY_COLORS = {
    "Minor": "#22c55e",
    "Moderate": "#f59e0b",
    "Severe": "#ef4444",
    "Requires Medical Attention": "#7c3aed",
    "None": "#6b7280",
}

# ── page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Incident Report System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    color: #e2e8f0;
}

/* Header */
.app-header {
    text-align: center;
    padding: 2rem 0 1rem;
}
.app-header h1 {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #818cf8, #c084fc, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.app-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 0.4rem;
}

/* Metric cards */
.metric-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    backdrop-filter: blur(8px);
}
.metric-card .label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin-bottom: 0.3rem;
}
.metric-card .value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #e2e8f0;
}
.metric-card.danger .value { color: #f87171; }
.metric-card.success .value { color: #34d399; }
.metric-card.info .value { color: #60a5fa; }

/* Severity badge */
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Form container */
div[data-testid="stForm"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(6px);
}

/* Section header */
.section-header {
    font-size: 1rem;
    font-weight: 600;
    color: #a5b4fc;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-bottom: 1px solid rgba(165,180,252,0.25);
    padding-bottom: 0.4rem;
    margin: 1.2rem 0 0.8rem;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(129,140,248,0.25) !important;
    color: #a5b4fc !important;
}

/* Dataframe */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Success / error */
.stAlert { border-radius: 12px !important; }

/* Input fields */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.12) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}

/* Required star */
.req { color: #f87171; }
</style>
""", unsafe_allow_html=True)

# ── helpers ──────────────────────────────────────────────────────────────────

def load_df() -> pd.DataFrame:
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        if "Submitted At" in df.columns:
            df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors="coerce")
        return df
    return pd.DataFrame()


def save_df(df: pd.DataFrame):
    df.to_csv(FILE_NAME, index=False)


def severity_badge(sev: str) -> str:
    color = SEVERITY_COLORS.get(sev, "#6b7280")
    return f'<span class="badge" style="background:{color}22;color:{color};border:1px solid {color}55">{sev}</span>'


def generate_pdf(row: dict) -> bytes:
    """Build a formatted PDF for a single incident report row."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=4,
        textColor=colors.HexColor("#312e81"),
    )
    story.append(Paragraph("📋 Incident Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}",
        ParagraphStyle("sub", fontSize=9, textColor=colors.grey, spaceAfter=12),
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#6366f1"), spaceAfter=14))

    def section(title: str, pairs: list[tuple]):
        story.append(Paragraph(title, ParagraphStyle(
            "SecHead", fontSize=11, fontName="Helvetica-Bold",
            textColor=colors.HexColor("#4f46e5"), spaceBefore=10, spaceAfter=4,
        )))
        data = [[Paragraph(f"<b>{k}</b>", styles["Normal"]),
                 Paragraph(str(v) if v else "—", styles["Normal"])]
                for k, v in pairs]
        t = Table(data, colWidths=[2.2 * inch, 4.8 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ede9fe")),
            ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.white, colors.HexColor("#f5f3ff")]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c4b5fd")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BORDERRADIUS", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)

    section("Basic Information", [
        ("Client Name", row.get("Client Name")),
        ("Incident Date", row.get("Incident Date")),
        ("Staff Reporting", row.get("Staff Reporting")),
        ("Witness", row.get("Witness")),
    ])
    section("Incident Details", [
        ("Medical Emergency", row.get("Medical Emergency")),
        ("Client Injury", f"{row.get('Client Injury')} — {row.get('Client Injury Desc')}"),
        ("Staff Injury", f"{row.get('Staff Injury')} — {row.get('Staff Injury Desc')}"),
        ("Property Damage", f"{row.get('Property Damage')} — {row.get('Property Damage Desc')}"),
        ("Other Notes", row.get("Other Report")),
    ])
    section("Body Check", [
        ("Body Locations", row.get("Body Locations")),
        ("Injury Types", row.get("Injury Types")),
        ("Severity", row.get("Severity")),
    ])
    section("Abuse / Actions / Notifications", [
        ("Abuse Suspected", row.get("Abuse Suspected")),
        ("Signs Observed", row.get("Abuse Signs")),
        ("Actions Taken", row.get("Actions Taken")),
        ("Supervisor Notified", f"{row.get('Supervisor Notified')} @ {row.get('Notification Time')}"),
        ("CPS Notified", row.get("CPS Notified")),
        ("Guardian Notified", f"{row.get('Guardian Notified')} @ {row.get('Guardian Time')}"),
        ("Witness Statement", row.get("Witness Statement")),
    ])
    section("Signatures", [
        ("Prepared By", row.get("Prepared By")),
        ("Report Date", row.get("Report Date")),
        ("Reviewed By", row.get("Reviewed By")),
        ("Supervisor Signature", row.get("Supervisor Signature")),
        ("Submitted At", str(row.get("Submitted At"))),
    ])

    doc.build(story)
    return buffer.getvalue()

# ── header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>📋 Incident Report System</h1>
  <p>Secure · Organized · Compliant</p>
</div>
""", unsafe_allow_html=True)

# ── tabs ─────────────────────────────────────────────────────────────────────
tab_form, tab_reports, tab_analytics = st.tabs(["📝 New Report", "📁 View Reports", "📊 Analytics"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FORM
# ══════════════════════════════════════════════════════════════════════════════
with tab_form:

    # ── dashboard metrics ────────────────────────────────────────────────────
    df_all = load_df()
    total = len(df_all)
    high_risk = int((df_all["Severity"] == "Severe").sum()) if "Severity" in df_all.columns else 0
    today_count = (
        int((df_all["Submitted At"].dt.date == datetime.now().date()).sum())
        if not df_all.empty and "Submitted At" in df_all.columns
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card info"><div class="label">Total Reports</div><div class="value">{total}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card danger"><div class="label">Severe Cases</div><div class="value">{high_risk}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card success"><div class="label">Submitted Today</div><div class="value">{today_count}</div></div>', unsafe_allow_html=True)
    open_abuse = int((df_all["Abuse Suspected"] == "Yes").sum()) if "Abuse Suspected" in df_all.columns else 0
    c4.markdown(f'<div class="metric-card danger"><div class="label">Abuse Flagged</div><div class="value">{open_abuse}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── form ─────────────────────────────────────────────────────────────────
    with st.form("incident_form", clear_on_submit=True):

        st.markdown('<div class="section-header">🧾 Basic Information</div>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            client_name     = st.text_input("Client Name *")
            incident_date   = st.date_input("Date of Incident")
        with col_b:
            staff_reporting = st.text_input("Staff Reporting *")
            witness         = st.text_input("Witness (if applicable)")

        st.markdown('<div class="section-header">🚨 Incident Details</div>', unsafe_allow_html=True)
        col_c, col_d = st.columns(2)
        with col_c:
            medical_emergency = st.selectbox("Medical Emergency", ["None", "Seizure", "Allergic Reaction", "Difficulty Breathing", "Other"])
            medical_other = st.text_input("Specify Medical Emergency") if medical_emergency == "Other" else ""

            client_injury      = st.selectbox("Client Injury Severity", ["None", "Minor", "Moderate", "Severe"])
            client_injury_desc = st.text_input("Client Injury Description")
        with col_d:
            staff_injury       = st.selectbox("Staff Injury Severity", ["None", "Minor", "Moderate", "Severe"])
            staff_injury_desc  = st.text_input("Staff Injury Description")

            property_damage      = st.selectbox("Property Damage", ["No", "Yes"])
            property_damage_desc = st.text_input("Describe Property Damage") if property_damage == "Yes" else ""

        other_report = st.text_area("Other Notes", height=80)

        st.markdown('<div class="section-header">🩺 Body Check</div>', unsafe_allow_html=True)
        col_e, col_f = st.columns(2)
        with col_e:
            body_locations = st.multiselect("Location of Injuries", ["Head","Face","Neck","Shoulders","Arms","Hands","Chest","Back","Abdomen","Hips","Legs","Feet","Other"])
            body_other = st.text_input("Specify Other Location") if "Other" in body_locations else ""
        with col_f:
            injury_types = st.multiselect("Injury Types", ["Bruising","Scratches","Cuts","Swelling","Redness","Abrasions","Bites","Broken Skin","Other"])
            injury_other = st.text_input("Specify Other Injury Type") if "Other" in injury_types else ""

        severity = st.selectbox("Severity of Injury", SEVERITY_ORDER)

        st.markdown('<div class="section-header">⚠️ Abuse / Actions / Signatures</div>', unsafe_allow_html=True)
        col_g, col_h = st.columns(2)
        with col_g:
            abuse       = st.selectbox("Was Abuse Suspected?", ["No", "Yes"])
            abuse_signs = st.text_area("Signs Observed", height=80)

            actions_taken = st.multiselect("Actions Taken", ["Cleaned wound","Applied bandage","Applied ice pack","Called first responders","Other"])
            actions_other = st.text_input("Specify Other Action") if "Other" in actions_taken else ""

        with col_h:
            supervisor_notified = st.selectbox("Supervisor Notified", ["No", "Yes"])
            cps_notified        = st.selectbox("CPS Notified", ["No", "Yes"])
            notif_time          = st.text_input("Notification Time")

            guardian_notified = st.selectbox("Guardian Notified", ["No", "Yes"])
            guardian_time     = st.text_input("Guardian Notification Time")

        witness_statement    = st.text_area("Witness Statement", height=80)

        col_i, col_j = st.columns(2)
        with col_i:
            prepared_by          = st.text_input("Prepared By")
            report_date          = st.date_input("Report Date")
        with col_j:
            reviewed_by          = st.text_input("Reviewed By")
            supervisor_signature = st.text_input("Supervisor Signature")

        submitted = st.form_submit_button("✅ Submit Report", use_container_width=True)

    # ── save ─────────────────────────────────────────────────────────────────
    if submitted:
        errors = []
        if not client_name.strip():
            errors.append("Client Name is required.")
        if not staff_reporting.strip():
            errors.append("Staff Reporting is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            new_row = {
                "Client Name": client_name, "Incident Date": incident_date,
                "Staff Reporting": staff_reporting, "Witness": witness,
                "Medical Emergency": medical_emergency, "Medical Other": medical_other,
                "Client Injury": client_injury, "Client Injury Desc": client_injury_desc,
                "Staff Injury": staff_injury, "Staff Injury Desc": staff_injury_desc,
                "Property Damage": property_damage, "Property Damage Desc": property_damage_desc,
                "Other Report": other_report,
                "Body Locations": ", ".join(body_locations), "Body Other": body_other,
                "Injury Types": ", ".join(injury_types), "Injury Other": injury_other,
                "Severity": severity,
                "Abuse Suspected": abuse, "Abuse Signs": abuse_signs,
                "Actions Taken": ", ".join(actions_taken), "Actions Other": actions_other,
                "Supervisor Notified": supervisor_notified, "CPS Notified": cps_notified,
                "Notification Time": notif_time,
                "Guardian Notified": guardian_notified, "Guardian Time": guardian_time,
                "Witness Statement": witness_statement,
                "Prepared By": prepared_by, "Report Date": report_date,
                "Reviewed By": reviewed_by, "Supervisor Signature": supervisor_signature,
                "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            df_new = pd.DataFrame([new_row])
            df_existing = load_df()
            if not df_existing.empty:
                df_new = pd.concat([df_existing, df_new], ignore_index=True)
            save_df(df_new)
            st.success("✅ Incident Report Submitted Successfully!")
            st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — VIEW REPORTS
# ══════════════════════════════════════════════════════════════════════════════
with tab_reports:
    df = load_df()

    if df.empty:
        st.info("No reports submitted yet. Use the **New Report** tab to get started.")
    else:
        # ── filters ──────────────────────────────────────────────────────────
        st.markdown("#### 🔍 Filter Reports")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            search_client = st.text_input("Search by Client Name", placeholder="Type to filter…")
        with fc2:
            filter_severity = st.multiselect("Filter by Severity", SEVERITY_ORDER)
        with fc3:
            filter_abuse = st.selectbox("Abuse Suspected", ["All", "Yes", "No"])

        filtered = df.copy()
        if search_client:
            filtered = filtered[filtered["Client Name"].str.contains(search_client, case=False, na=False)]
        if filter_severity:
            filtered = filtered[filtered["Severity"].isin(filter_severity)]
        if filter_abuse != "All":
            filtered = filtered[filtered["Abuse Suspected"] == filter_abuse]

        st.markdown(f"**{len(filtered)}** record(s) shown")

        # ── table ────────────────────────────────────────────────────────────
        display_cols = ["Client Name", "Incident Date", "Staff Reporting",
                        "Severity", "Abuse Suspected", "Submitted At"]
        show_cols = [c for c in display_cols if c in filtered.columns]
        st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)

        # ── per-row actions ──────────────────────────────────────────────────
        st.markdown("#### 🗂 Report Actions")
        row_labels = [
            f"#{i} — {row.get('Client Name','?')} ({row.get('Incident Date','?')})"
            for i, row in filtered.iterrows()
        ]
        if row_labels:
            selected_label = st.selectbox("Select a report", row_labels)
            selected_idx   = int(selected_label.split("—")[0].replace("#", "").strip())
            selected_row   = filtered.loc[selected_idx].to_dict()

            col_act1, col_act2 = st.columns(2)

            with col_act1:
                if REPORTLAB_OK:
                    pdf_bytes = generate_pdf(selected_row)
                    fname = f"incident_{selected_row.get('Client Name','report').replace(' ','_')}_{selected_row.get('Incident Date','')}.pdf"
                    st.download_button(
                        "⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=fname,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.warning("Install `reportlab` for PDF export: `pip install reportlab`")

            with col_act2:
                if st.button("🗑 Delete This Report", use_container_width=True, type="secondary"):
                    df_full = load_df()
                    df_full = df_full.drop(index=selected_idx).reset_index(drop=True)
                    save_df(df_full)
                    st.success("Report deleted.")
                    st.rerun()

        # ── download all CSV ─────────────────────────────────────────────────
        st.download_button(
            "⬇️ Export All Reports (CSV)",
            data=filtered.to_csv(index=False).encode(),
            file_name="incident_reports_export.csv",
            mime="text/csv",
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    df = load_df()

    if df.empty:
        st.info("Submit some reports to see analytics.")
    elif not PLOTLY_OK:
        st.warning("Install `plotly` for charts: `pip install plotly`")
    else:
        st.markdown("### 📊 Incident Analytics")

        ac1, ac2 = st.columns(2)

        with ac1:
            # Severity distribution
            if "Severity" in df.columns:
                sev_counts = df["Severity"].value_counts().reset_index()
                sev_counts.columns = ["Severity", "Count"]
                fig1 = px.pie(
                    sev_counts, names="Severity", values="Count",
                    title="Injury Severity Breakdown",
                    color="Severity",
                    color_discrete_map={
                        "Minor": "#22c55e", "Moderate": "#f59e0b",
                        "Severe": "#ef4444", "Requires Medical Attention": "#7c3aed",
                    },
                    hole=0.45,
                )
                fig1.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e2e8f0",
                    legend_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig1, use_container_width=True)

        with ac2:
            # Medical emergency types
            if "Medical Emergency" in df.columns:
                med_counts = df[df["Medical Emergency"] != "None"]["Medical Emergency"].value_counts().reset_index()
                med_counts.columns = ["Type", "Count"]
                if not med_counts.empty:
                    fig2 = px.bar(
                        med_counts, x="Count", y="Type", orientation="h",
                        title="Medical Emergencies by Type",
                        color="Count",
                        color_continuous_scale=["#818cf8", "#c084fc"],
                    )
                    fig2.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#e2e8f0",
                        coloraxis_showscale=False,
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No medical emergencies recorded yet.")

        # Timeline
        if "Submitted At" in df.columns:
            df["Date"] = df["Submitted At"].dt.date
            timeline = df.groupby("Date").size().reset_index(name="Reports")
            fig3 = px.area(
                timeline, x="Date", y="Reports",
                title="Reports Over Time",
                color_discrete_sequence=["#818cf8"],
            )
            fig3.update_traces(fill="tozeroy", fillcolor="rgba(129,140,248,0.15)")
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                xaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
            )
            st.plotly_chart(fig3, use_container_width=True)

        # Abuse flag summary
        if "Abuse Suspected" in df.columns:
            ab_yes = int((df["Abuse Suspected"] == "Yes").sum())
            ab_no  = int((df["Abuse Suspected"] == "No").sum())
            st.markdown(f"""
            <div style="display:flex;gap:1rem;margin-top:0.5rem">
              <div class="metric-card danger" style="flex:1">
                <div class="label">Abuse Suspected</div>
                <div class="value">{ab_yes}</div>
              </div>
              <div class="metric-card success" style="flex:1">
                <div class="label">No Abuse</div>
                <div class="value">{ab_no}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)