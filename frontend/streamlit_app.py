import os
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── Configuration ──────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_URL", "http://localhost:8000")
MATCH_URL = f"{API_BASE}/api/match"
HISTORY_URL = f"{API_BASE}/api/history"

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume ↔ JD Matcher",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .score-box {
        text-align: center;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .score-excellent { background: #d4edda; color: #155724; }
    .score-good      { background: #cce5ff; color: #004085; }
    .score-average   { background: #fff3cd; color: #856404; }
    .score-low       { background: #f8d7da; color: #721c24; }
    .skill-chip {
        display: inline-block;
        padding: 2px 10px;
        margin: 3px;
        border-radius: 20px;
        font-size: 0.85em;
    }
    .chip-match   { background: #28a745; color: white; }
    .chip-missing { background: #dc3545; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("AI Resume Matcher")
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. Upload your resume (PDF/DOCX)")
    st.markdown("2. Paste the job description")
    st.markdown("3. Click **Analyze** for instant results")
    st.markdown("---")

    # Health check in sidebar
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        if r.status_code == 200:
            data = r.json()
            st.success(f"✅ API: Online | DB: {data.get('database', 'unknown')}")
        else:
            st.warning("⚠️ API reachable but returned an error")
    except Exception:
        st.error("❌ API is offline — check Docker is running")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_analyze, tab_history = st.tabs(["🔍 Analyze Resume", "📋 Match History"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — Analyze
# ════════════════════════════════════════════════════════════════════════════════
with tab_analyze:
    st.header("🔍 Resume ↔ Job Description Matcher")

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("📄 Upload Resume")
        uploaded_resume = st.file_uploader(
            "Choose your resume (PDF or DOCX)",
            type=["pdf", "docx"],
            help="Supported formats: PDF, DOCX",
        )
        candidate_name = st.text_input(
            "Candidate Name (optional)",
            placeholder="e.g. Priya Sharma",
        )

    with col_right:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Paste the full job description here",
            height=220,
            placeholder="We are looking for a Python developer with experience in FastAPI, Docker, and PostgreSQL...",
        )

    st.markdown("---")
    analyze_btn = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

    if analyze_btn:
        if not uploaded_resume:
            st.warning("⚠️ Please upload your resume (PDF or DOCX).")
        elif not job_description.strip():
            st.warning("⚠️ Please paste the job description.")
        else:
            with st.spinner("⏳ Analyzing your resume... this may take a moment on first run."):
                try:
                    files = {
                        "resume": (
                            uploaded_resume.name,
                            uploaded_resume.getvalue(),
                            "application/octet-stream",
                        )
                    }
                    data = {
                        "job_description": job_description,
                        "candidate_name": candidate_name,
                    }
                    response = requests.post(MATCH_URL, files=files, data=data, timeout=120)

                    if response.status_code == 200:
                        result = response.json()
                        score = result["score"]
                        matched = result["matched_skills"]
                        missing = result["missing_skills"]
                        recs = result["recommendations"]

                        # ── Score display ──────────────────────────────────────
                        if score >= 75:
                            css_class, label = "score-excellent", "Excellent Match 🎉"
                        elif score >= 55:
                            css_class, label = "score-good", "Good Match 👍"
                        elif score >= 35:
                            css_class, label = "score-average", "Moderate Match ⚠️"
                        else:
                            css_class, label = "score-low", "Low Match ❌"

                        st.markdown(
                            f'<div class="score-box {css_class}">'
                            f'<h1>{score}%</h1><h3>{label}</h3></div>',
                            unsafe_allow_html=True,
                        )

                        # ── Gauge chart ────────────────────────────────────────
                        fig = go.Figure(
                            go.Indicator(
                                mode="gauge+number",
                                value=score,
                                title={"text": "Match Score"},
                                gauge={
                                    "axis": {"range": [0, 100]},
                                    "bar": {"color": "#4CAF50" if score >= 55 else "#FF5722"},
                                    "steps": [
                                        {"range": [0, 35], "color": "#ffcccc"},
                                        {"range": [35, 55], "color": "#fff3cc"},
                                        {"range": [55, 75], "color": "#cce5ff"},
                                        {"range": [75, 100], "color": "#d4edda"},
                                    ],
                                    "threshold": {
                                        "line": {"color": "black", "width": 3},
                                        "thickness": 0.75,
                                        "value": score,
                                    },
                                },
                                number={"suffix": "%"},
                            )
                        )
                        fig.update_layout(height=280, margin=dict(t=40, b=0, l=20, r=20))
                        st.plotly_chart(fig, use_container_width=True)

                        # ── Skills breakdown ───────────────────────────────────
                        c1, c2 = st.columns(2)
                        with c1:
                            st.subheader(f"✅ Matched Skills ({len(matched)})")
                            if matched:
                                chips = " ".join(
                                    f'<span class="skill-chip chip-match">{s}</span>'
                                    for s in matched
                                )
                                st.markdown(chips, unsafe_allow_html=True)
                            else:
                                st.info("No matching skills detected.")

                        with c2:
                            st.subheader(f"❌ Missing Skills ({len(missing)})")
                            if missing:
                                chips = " ".join(
                                    f'<span class="skill-chip chip-missing">{s}</span>'
                                    for s in missing
                                )
                                st.markdown(chips, unsafe_allow_html=True)
                            else:
                                st.success("No missing skills — great fit!")

                        # ── Recommendations ────────────────────────────────────
                        st.markdown("---")
                        st.subheader("💡 Personalized Recommendations")
                        if recs:
                            for rec in recs:
                                st.info(rec)
                        else:
                            st.success(
                                "🎉 Your resume covers all the skills in this job description!"
                            )

                        # ── Skills pie chart ───────────────────────────────────
                        if matched or missing:
                            st.markdown("---")
                            st.subheader("📊 Skills Coverage")
                            pie = go.Figure(
                                go.Pie(
                                    labels=["Matched", "Missing"],
                                    values=[len(matched), len(missing)],
                                    marker_colors=["#28a745", "#dc3545"],
                                    hole=0.4,
                                )
                            )
                            pie.update_layout(height=300, margin=dict(t=20, b=0, l=0, r=0))
                            st.plotly_chart(pie, use_container_width=True)

                    else:
                        try:
                            err_detail = response.json().get("detail", response.text)
                        except Exception:
                            err_detail = response.text
                        st.error(f"❌ API Error {response.status_code}: {err_detail}")

                except requests.exceptions.ConnectionError:
                    st.error(
                        "❌ Cannot connect to the backend API. "
                        "Make sure Docker is running and the containers are up."
                    )
                except requests.exceptions.Timeout:
                    st.error(
                        "⏳ The request timed out. "
                        "The model might be loading for the first time — please try again."
                    )
                except Exception as e:
                    st.error(f"❌ Unexpected error: {e}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — History
# ════════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.header("📋 Match History")
    refresh_btn = st.button("🔄 Refresh History")

    try:
        hist_resp = requests.get(HISTORY_URL, timeout=10)
        if hist_resp.status_code == 200:
            records = hist_resp.json()
            if records:
                df = pd.DataFrame(records)
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime(
                    "%Y-%m-%d %H:%M"
                )
                df["matched_skills"] = df["matched_skills"].apply(
                    lambda x: ", ".join(x) if isinstance(x, list) else x
                )
                df["missing_skills"] = df["missing_skills"].apply(
                    lambda x: ", ".join(x) if isinstance(x, list) else x
                )
                display_cols = [
                    "id", "candidate_name", "resume_filename",
                    "score", "matched_skills", "missing_skills", "created_at",
                ]
                st.dataframe(
                    df[display_cols].rename(
                        columns={
                            "id": "ID",
                            "candidate_name": "Candidate",
                            "resume_filename": "File",
                            "score": "Score (%)",
                            "matched_skills": "Matched Skills",
                            "missing_skills": "Missing Skills",
                            "created_at": "Analysed At",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No match history yet. Run your first analysis above!")
        else:
            st.warning(f"Could not fetch history: {hist_resp.status_code}")
    except Exception as e:
        st.error(f"Could not load history: {e}")
