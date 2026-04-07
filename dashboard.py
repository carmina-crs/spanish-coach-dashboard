"""
My Daily Spanish – Coach Applications Dashboard
================================================
Reads application records from Supabase (written by the main portal app).

Run locally:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SUPABASE_URL = st.secrets.get("supabase_url", "")
SUPABASE_KEY = st.secrets.get("supabase_key", "")

st.set_page_config(
    page_title="Coach Applications Dashboard",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .dashboard-header {
        background: linear-gradient(135deg, #1a5276, #2980b9);
        color: white; padding: 1.5rem 2rem; border-radius: 10px; margin-bottom: 1.5rem;
    }
    .dashboard-header h1 { color: white; margin: 0; font-size: 1.8rem; }
    .dashboard-header p  { color: #d6eaf8; margin: 0.3rem 0 0 0; font-size: 1rem; }

    .metric-card {
        background: white; border: 1px solid #e0e0e0; border-radius: 10px;
        padding: 1.2rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-card .number { font-size: 2rem; font-weight: 700; color: #1a5276; }
    .metric-card .label  { font-size: 0.85rem; color: #7f8c8d; margin-top: 0.2rem; }

    .badge-recommended {
        background: #27ae60; color: white; padding: 3px 10px;
        border-radius: 12px; font-size: 0.8rem; font-weight: 600;
    }
    .badge-maybe {
        background: #f39c12; color: white; padding: 3px 10px;
        border-radius: 12px; font-size: 0.8rem; font-weight: 600;
    }
    .badge-not-recommended {
        background: #e74c3c; color: white; padding: 3px 10px;
        border-radius: 12px; font-size: 0.8rem; font-weight: 600;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Nice column labels (JSON key → display name)
# ---------------------------------------------------------------------------
COLUMN_LABELS = {
    "submission_date": "Submission Date",
    "name": "Name",
    "email": "Email",
    "age": "Age",
    "country_origin": "Country of Origin",
    "current_location": "Current Location",
    "timezone": "Time Zone",
    "mobile": "Mobile",
    "whatsapp": "WhatsApp",
    "address": "Address",
    "tax_info": "Tax Information",
    "payment_pref": "Payment Preference",
    "teaching_schedule": "Teaching Schedule",
    "profile_link": "Profile Link",
    "native_spanish": "Native Speaker",
    "spanish_type": "Type of Spanish",
    "years_teaching": "Years Teaching",
    "certifications": "Certifications",
    "students_taught": "Students Taught",
    "all_levels": "Teach A1-C2",
    "levels_detail": "Levels Detail",
    "dele_exp": "DELE Experience",
    "dele_detail": "DELE Detail",
    "current_platforms": "Current Platforms",
    "testimonial_link": "Testimonial Link",
    "english_level": "English Level",
    "ideal_rate": "Ideal Rate (USD)",
    "ai_score": "Score",
    "ai_verdict": "Verdict",
    "ai_summary": "Summary",
    "video_mode": "Video Mode",
    "video_link": "Video Link",
    "files_link": "Files Link",
    "has_cv": "CV",
    "has_certificates": "Certificates",
    "has_video": "Video",
    # Step 5 — Teaching Philosophy
    "assess_proficiency": "How do you assess proficiency?",
    "tailor_lessons": "How do you tailor lessons?",
    "successful_lesson": "Successful lesson example",
    "engaging_online": "Keeping online lessons engaging",
    "student_duration": "Student retention",
    "motivate_struggling": "Motivating struggling students",
    "enjoy_process": "What do you enjoy about teaching?",
    # Step 6 — Technology & Assessment
    "multimedia": "Multimedia & cultural content",
    "tech_setup": "Tech setup (mic, webcam, internet)",
    "software": "Software / platforms used",
    "assess_progress": "Assessing student progress",
    "feedback_style": "Feedback style",
    "adapt_teaching": "Adapting teaching approach",
    "cultural_lesson": "Cultural lesson example",
    # Step 7 — Professional Development
    "improve_skills": "How do you improve your skills?",
    "excited_areas": "Excited areas of teaching",
    "grammar_error": "Grammar error approach",
    "lesson_plan_levels": "Lesson plan for different levels",
    # Step 8 — Team & Communication
    "handle_criticism": "Handling criticism",
    "teamwork": "Teamwork comfort",
    "follow_process": "Comfortable following set process",
    "first_session_win": "First session quick win",
    "session_notes_ok": "Session notes & tracker updates",
    "respond_24h": "Respond within 24h",
    "hours_per_week": "Hours per week",
    # Step 9 — Quiz
    "quiz_1": "Quiz Q1",
    "quiz_2": "Quiz Q2",
    "quiz_3": "Quiz Q3",
    "quiz_4": "Quiz Q4",
    "quiz_5": "Quiz Q5",
    "quiz_6": "Quiz Q6",
    "quiz_7": "Quiz Q7",
    "quiz_8": "Quiz Q8",
    "quiz_9": "Quiz Q9",
    "quiz_10": "Quiz Q10",
    "quiz_11": "Quiz Q11",
    "quiz_12": "Quiz Q12",
}

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_applications():
    """Load application records from Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return pd.DataFrame()

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/applications?select=*&order=id.desc",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df.drop(columns=["id"], errors="ignore", inplace=True)
        df.rename(columns=COLUMN_LABELS, inplace=True)
        return df
    except Exception:
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Dashboard components
# ---------------------------------------------------------------------------

def render_metrics(df):
    total = len(df)
    recommended = maybe = not_rec = 0
    if "Verdict" in df.columns:
        verdicts = df["Verdict"].str.strip().str.upper()
        recommended = (verdicts == "RECOMMENDED").sum()
        maybe = (verdicts == "MAYBE").sum()
        not_rec = (verdicts == "NOT RECOMMENDED").sum()

    cols = st.columns(4)
    with cols[0]:
        st.markdown(f'<div class="metric-card"><div class="number">{total}</div>'
                     f'<div class="label">Total Applications</div></div>',
                     unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="metric-card"><div class="number" style="color:#27ae60">{recommended}</div>'
                     f'<div class="label">Recommended</div></div>',
                     unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="metric-card"><div class="number" style="color:#f39c12">{maybe}</div>'
                     f'<div class="label">Maybe</div></div>',
                     unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f'<div class="metric-card"><div class="number" style="color:#e74c3c">{not_rec}</div>'
                     f'<div class="label">Not Recommended</div></div>',
                     unsafe_allow_html=True)


def render_filters(df):
    st.sidebar.markdown("## Filters")
    filtered = df.copy()

    # Search
    search = st.sidebar.text_input("Search (name or email):", "")
    if search:
        mask = (
            filtered.get("Name", pd.Series(dtype=str)).str.contains(search, case=False, na=False) |
            filtered.get("Email", pd.Series(dtype=str)).str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    # Verdict filter
    if "Verdict" in filtered.columns:
        verdicts = sorted(filtered["Verdict"].dropna().unique())
        verdicts = [v for v in verdicts if v.strip()]
        if verdicts:
            selected = st.sidebar.multiselect("Verdict:", verdicts, default=verdicts)
            filtered = filtered[filtered["Verdict"].isin(selected)]

    # Country filter
    if "Country of Origin" in filtered.columns:
        countries = sorted(filtered["Country of Origin"].dropna().unique())
        countries = [c for c in countries if c.strip()]
        if countries:
            selected = st.sidebar.multiselect("Country:", countries)
            if selected:
                filtered = filtered[filtered["Country of Origin"].isin(selected)]

    # Type of Spanish filter
    if "Type of Spanish" in filtered.columns:
        types = sorted(filtered["Type of Spanish"].dropna().unique())
        types = [t for t in types if t.strip()]
        if types:
            selected = st.sidebar.multiselect("Type of Spanish:", types)
            if selected:
                filtered = filtered[filtered["Type of Spanish"].isin(selected)]

    # Score range
    if "Score" in filtered.columns:
        scores = pd.to_numeric(filtered["Score"], errors="coerce")
        if scores.notna().any():
            mn, mx = int(scores.min()), int(scores.max())
            if mn < mx:
                rng = st.sidebar.slider("Score range:", mn, mx, (mn, mx))
                filtered = filtered[scores.between(rng[0], rng[1]) | scores.isna()]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Showing {len(filtered)} of {len(df)} applications**")
    return filtered


def render_table(df):
    st.markdown("### Applications")

    if df.empty:
        st.info("No applications match the current filters.")
        return

    summary_cols = [
        "Submission Date", "Name", "Email", "Country of Origin",
        "Type of Spanish", "Years Teaching", "Ideal Rate (USD)", "Score", "Verdict",
        "CV", "Certificates", "Video",
    ]
    available = [c for c in summary_cols if c in df.columns]

    st.dataframe(
        df[available],
        use_container_width=True,
        hide_index=True,
        height=min(400, 50 + 35 * len(df)),
    )

    csv = df.to_csv(index=False)
    st.download_button(
        "Download as CSV",
        csv,
        f"coach_applications_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
    )


# ---------------------------------------------------------------------------
# PDF Generation
# ---------------------------------------------------------------------------

# Full question text exactly as shown in the portal (for PDF output)
PDF_SECTIONS = [
    ("Personal Information", [
        ("Full Name", "Name"),
        ("Email", "Email"),
        ("Age", "Age"),
        ("Country of Origin", "Country of Origin"),
        ("Current Location", "Current Location"),
        ("Time Zone", "Time Zone"),
        ("Mobile Number", "Mobile"),
        ("WhatsApp Number", "WhatsApp"),
        ("Address", "Address"),
    ]),
    ("Employment Details", [
        ("Tax Information", "Tax Information"),
        ("Payment Preference", "Payment Preference"),
        ("Teaching Schedule / Availability", "Teaching Schedule"),
        ("Online Profile Link", "Profile Link"),
        ("English Level", "English Level"),
        ("Ideal Hourly Rate (USD)", "Ideal Rate (USD)"),
        ("Preferred Hours per Week", "Hours per week"),
    ]),
    ("Teaching Background", [
        ("Are you a native Spanish speaker?", "Native Speaker"),
        ("What type/variety of Spanish do you speak?", "Type of Spanish"),
        ("Years of Spanish teaching experience", "Years Teaching"),
        ("Teaching certifications / qualifications", "Certifications"),
        ("How many students have you taught?", "Students Taught"),
        ("Can you teach all levels (A1-C2)?", "Teach A1-C2"),
        ("If not all levels, which levels?", "Levels Detail"),
        ("Do you have DELE exam preparation experience?", "DELE Experience"),
        ("DELE experience details", "DELE Detail"),
        ("Current/previous teaching platforms", "Current Platforms"),
        ("Testimonial / review link", "Testimonial Link"),
    ]),
    ("Teaching Philosophy, Engagement & Motivation (Step 5)", [
        ("1. How do you assess a student's proficiency in Spanish before starting lessons?", "How do you assess proficiency?"),
        ("2. How do you tailor your lessons to suit different learning styles and proficiency levels?", "How do you tailor lessons?"),
        ("3. Can you give an example of a particularly successful lesson or course you've delivered? What made it effective?", "Successful lesson example"),
        ("4. How do you keep online lessons engaging and interactive for students?", "Keeping online lessons engaging"),
        ("5. How long do students typically stay with you, and what do you think contributes to student retention?", "Student retention"),
        ("6. How do you motivate students who are struggling or losing interest?", "Motivating struggling students"),
        ("7. What do you enjoy most about the teaching process?", "What do you enjoy about teaching?"),
    ]),
    ("Technology, Assessment & Adapting to Challenges (Step 6)", [
        ("1. Do you incorporate multimedia resources or cultural content into your lessons? If yes, examples?", "Multimedia & cultural content"),
        ("2. Do you have a quality microphone, webcam, stable internet connection, and a quiet, well-lit workspace?", "Tech setup (mic, webcam, internet)"),
        ("3. Which software or platforms do you use for conducting online classes?", "Software / platforms used"),
        ("4. How do you assess your students' progress, and how often do you provide updates or evaluations?", "Assessing student progress"),
        ("5. How do you provide constructive and motivating feedback to your students?", "Feedback style"),
        ("6. Can you share an example of a time when you had to adapt your teaching approach to meet the needs of a particularly challenging student?", "Adapting teaching approach"),
        ("7. Can you give an example of a cultural lesson or activity that you believe is essential for students learning Spanish?", "Cultural lesson example"),
    ]),
    ("Professional Development & Scenarios (Step 7)", [
        ("1. How do you continue to improve your Spanish teaching skills?", "How do you improve your skills?"),
        ("2. What areas of Spanish teaching excite you most?", "Excited areas of teaching"),
        ("3. How do you approach correcting a student's grammar errors?", "Grammar error approach"),
        ("4. How would you structure lesson plans for students of different levels?", "Lesson plan for different levels"),
    ]),
    ("Team, Communication & Rate (Step 8)", [
        ("1. How do you respond to constructive criticism from a supervisor?", "Handling criticism"),
        ("2. How comfortable are you working closely with a team?", "Teamwork comfort"),
        ("3. Are you comfortable following a set process rather than always doing things your own way?", "Comfortable following set process"),
        ("4. In our program, the first session must give the student a \"quick win\". How would you do this in practice?", "First session quick win"),
        ("5. Are you comfortable with session notes and tracker updates immediately after each session?", "Session notes & tracker updates"),
        ("6. Will you respond to student/team messages within 24 hours?", "Respond within 24h"),
    ]),
    ("Program Understanding Quiz (Step 9)", [
        ("1. What are the key commitments and promises we make to students enrolled in the program?", "Quiz Q1"),
        ("2. What should a coach do upon receiving a student's study plan from the team?", "Quiz Q2"),
        ("3. Describe what the 12-week study plan typically includes.", "Quiz Q3"),
        ("4. What should coaches do with the study plan every 2-3 weeks?", "Quiz Q4"),
        ("5. What are the weekly non-negotiable tasks assigned to students, and what is the coach's responsibility regarding these?", "Quiz Q5"),
        ("6. When and how should the coach reach out to the student upon receiving their details from the team?", "Quiz Q6"),
        ("7. How will you use the student details provided by the team (level, goals, interests, challenges) to prepare for your first session?", "Quiz Q7"),
        ("8. What is the goal of the first session, and what should it NOT be focused entirely on?", "Quiz Q8"),
        ("9. What is the purpose of the student profile sheet, and how often should it be updated?", "Quiz Q9"),
        ("10. Explain the BAMFAM approach and how it should be applied in sessions.", "Quiz Q10"),
        ("11. Who is responsible for checking and providing feedback on the student's essay exercises, and how should students submit their essays?", "Quiz Q11"),
        ("12. What is the expected response time for coaches to reply to student or team messages on weekdays and weekends?", "Quiz Q12"),
    ]),
    ("AI Assessment", [
        ("Overall Score", "Score"),
        ("Verdict", "Verdict"),
        ("Summary", "Summary"),
    ]),
    ("Files Submitted", [
        ("CV / Resume uploaded", "CV"),
        ("Certificates uploaded", "Certificates"),
        ("Video submitted", "Video"),
        ("Video Mode", "Video Mode"),
        ("Video Link", "Video Link"),
        ("Files Folder Link", "Files Link"),
    ]),
]


def _clean_text(text: str) -> str:
    """Replace problematic unicode characters for PDF (latin-1)."""
    replacements = {
        "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2192": "->", "\u2190": "<-",
        "\u2705": "[Yes]", "\u274c": "[No]",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Drop anything else that can't be encoded in latin-1
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_applicant_pdf(row) -> bytes:
    """Generate a PDF for a single applicant with all questions and answers."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_fill_color(26, 82, 118)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, _clean_text("Spanish Coach Application"), new_x="LMARGIN", new_y="NEXT", fill=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, _clean_text("My Daily Spanish"), new_x="LMARGIN", new_y="NEXT", fill=True, align="C")
    pdf.ln(4)

    # Applicant name banner
    name = str(row.get("Name", "Unknown"))
    submission = str(row.get("Submission Date", ""))
    pdf.set_fill_color(230, 240, 250)
    pdf.set_text_color(26, 82, 118)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, _clean_text(name), new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _clean_text(f"Submitted: {submission}"), new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(4)
    pdf.set_text_color(0, 0, 0)

    # Sections
    for section_name, qas in PDF_SECTIONS:
        # Section header
        pdf.set_fill_color(41, 128, 185)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, _clean_text(section_name), new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.ln(2)
        pdf.set_text_color(0, 0, 0)

        for question, field_key in qas:
            value = str(row.get(field_key, "")).strip()
            if not value or value.lower() == "nan":
                continue

            # Question
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 5, _clean_text(question))
            # Answer
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(0, 5, _clean_text(value))
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

        pdf.ln(3)

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)


def render_detail_view(df):
    st.markdown("### Applicant Details")

    if df.empty:
        return

    names = df.get("Name", pd.Series(dtype=str)).tolist()
    emails = df.get("Email", pd.Series(dtype=str)).tolist()
    options = [f"{n} ({e})" for n, e in zip(names, emails)]

    selected = st.selectbox("Select an applicant to view details:", options)
    if selected is None:
        return

    idx = options.index(selected)
    row = df.iloc[idx]

    # PDF download button
    try:
        pdf_bytes = generate_applicant_pdf(row)
        safe_name = str(row.get("Name", "applicant")).replace(" ", "_")
        st.download_button(
            "Download Application as PDF",
            data=pdf_bytes,
            file_name=f"application_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            type="primary",
        )
    except Exception as e:
        st.warning(f"PDF generation failed: {e}")

    sections = {
        "Personal Information": [
            "Name", "Email", "Age", "Country of Origin", "Current Location",
            "Time Zone", "Mobile", "WhatsApp", "Address",
        ],
        "Employment Details": [
            "Tax Information", "Payment Preference", "Teaching Schedule",
            "Profile Link", "English Level", "Ideal Rate (USD)",
            "Hours per week",
        ],
        "Teaching Background": [
            "Native Speaker", "Type of Spanish", "Years Teaching",
            "Certifications", "Students Taught", "Teach A1-C2", "Levels Detail",
            "DELE Experience", "DELE Detail", "Current Platforms",
            "Testimonial Link",
        ],
        "Teaching Philosophy (Step 5)": [
            "How do you assess proficiency?", "How do you tailor lessons?",
            "Successful lesson example", "Keeping online lessons engaging",
            "Student retention", "Motivating struggling students",
            "What do you enjoy about teaching?",
        ],
        "Technology & Assessment (Step 6)": [
            "Multimedia & cultural content", "Tech setup (mic, webcam, internet)",
            "Software / platforms used", "Assessing student progress",
            "Feedback style", "Adapting teaching approach",
            "Cultural lesson example",
        ],
        "Professional Development (Step 7)": [
            "How do you improve your skills?", "Excited areas of teaching",
            "Grammar error approach", "Lesson plan for different levels",
        ],
        "Team & Communication (Step 8)": [
            "Handling criticism", "Teamwork comfort",
            "Comfortable following set process", "First session quick win",
            "Session notes & tracker updates", "Respond within 24h",
        ],
        "Program Understanding Quiz (Step 9)": [
            "Quiz Q1", "Quiz Q2", "Quiz Q3", "Quiz Q4",
            "Quiz Q5", "Quiz Q6", "Quiz Q7", "Quiz Q8",
            "Quiz Q9", "Quiz Q10", "Quiz Q11", "Quiz Q12",
        ],
        "AI Assessment": [
            "Score", "Verdict", "Summary",
        ],
        "Media & Files": [
            "Video Mode", "Video Link", "Files Link",
        ],
    }

    link_fields = {"Video Link", "Files Link", "Profile Link", "Testimonial Link"}

    for section_name, fields in sections.items():
        available = [f for f in fields if f in row.index and str(row[f]).strip()]
        if not available:
            continue

        with st.expander(section_name, expanded=(section_name == "Personal Information")):
            for field in available:
                value = str(row[field])
                if field == "Verdict":
                    v = value.strip().upper()
                    badge = ("badge-recommended" if v == "RECOMMENDED"
                             else "badge-maybe" if v == "MAYBE"
                             else "badge-not-recommended")
                    st.markdown(f"**{field}:** <span class='{badge}'>{value}</span>",
                                unsafe_allow_html=True)
                elif field in link_fields and value.startswith("http"):
                    st.markdown(f"**{field}:** [{value}]({value})")
                elif field == "Summary":
                    st.markdown(f"**{field}:**")
                    st.text_area("", value, height=150, disabled=True,
                                 key=f"summary_{idx}_{field}")
                else:
                    st.markdown(f"**{field}:** {value}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.markdown("""
    <div class="dashboard-header">
        <h1>Coach Applications Dashboard</h1>
        <p>My Daily Spanish — View and manage coach applications</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_applications()

    if df.empty:
        st.info("No applications recorded yet. Applications will appear here "
                "after coaches submit through the portal.")
        return

    # Refresh
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Refresh", use_container_width=True):
            st.rerun()

    render_metrics(df)
    st.markdown("")

    filtered_df = render_filters(df)

    tab1, tab2 = st.tabs(["Table View", "Detail View"])
    with tab1:
        render_table(filtered_df)
    with tab2:
        render_detail_view(filtered_df)


if __name__ == "__main__":
    main()
