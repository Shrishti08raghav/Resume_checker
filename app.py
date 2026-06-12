# hr_dashboard.py
import streamlit as st
import PyPDF2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from database import init_db, save_result

init_db()

if "df" not in st.session_state:
    st.session_state.df = None
if "jd_keywords" not in st.session_state:
    st.session_state.jd_keywords = None

st.set_page_config(page_title="HR Dashboard", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .main-header {
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6a39cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 0.3rem;
        animation: fadeInDown 0.8s ease;
    }

    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 1.5rem;
        animation: fadeIn 1.2s ease;
    }

    @keyframes fadeInDown {
        from {opacity: 0; transform: translateY(-20px);}
        to {opacity: 1; transform: translateY(0);}
    }

    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }

    @keyframes fadeInUp {
        from {opacity: 0; transform: translateY(15px);}
        to {opacity: 1; transform: translateY(0);}
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3A0353, #804A8A, #F59E51);
        color: white;
        font-weight: 600;
        padding: 0.7rem;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 18px rgba(245, 158, 81, 0.4);
    }

    .stDownloadButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3A0353, #804A8A, #F59E51);
        color: white;
        font-weight: 600;
        padding: 0.7rem;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
    }

    .stDownloadButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 18px rgba(245, 158, 81, 0.4);
    }

    .metric-card {
        background: linear-gradient(135deg, #f5f7fa, #e4ecfb);
        padding: 1.2rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: fadeInUp 0.6s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(37, 117, 252, 0.2);
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2575fc;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #555;
    }

    .candidate-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 5px solid #2575fc;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        animation: fadeInUp 0.5s ease;
    }

    .candidate-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 16px rgba(37, 117, 252, 0.18);
        border-left: 5px solid #6a11cb;
    }

    .rank-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        color: white;
        background: linear-gradient(90deg, #6a11cb, #2575fc);
    }

    .gold { background: linear-gradient(90deg, #f7971e, #ffd200); color: #5a3e00; }
    .silver { background: linear-gradient(90deg, #bdc3c7, #2c3e50); }
    .bronze { background: linear-gradient(90deg, #cd7f32, #8b5a2b); }

    .chance-badge {
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        color: white;
    }

    .chance-high { background: linear-gradient(90deg, #11998e, #38ef7d); }
    .chance-medium { background: linear-gradient(90deg, #f7971e, #ffd200); color: #5a3e00; }
    .chance-low { background: linear-gradient(90deg, #e53935, #ff7043); }

    div[data-testid="stTabs"] button {
        transition: all 0.25s ease;
        border-radius: 8px 8px 0 0;
    }

    div[data-testid="stTabs"] button:hover {
        background-color: #eef2ff;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📊 HR Resume Ranking Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload a Job Description and resumes to instantly rank candidates by relevance ✨</p>', unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns(2)
with col1:
    jd_file = st.file_uploader("📄 Upload Job Description (PDF)", type="pdf")
with col2:
    resumes = st.file_uploader("👥 Upload Resumes (PDFs)", type="pdf", accept_multiple_files=True)

def get_text(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text().lower() for p in reader.pages if p.extract_text()])

def selection_chance(pct):
    """Returns (label, css_class) based on match percentage."""
    if pct >= 70:
        return "High Chance", "chance-high"
    elif pct >= 40:
        return "Medium Chance", "chance-medium"
    else:
        return "Low Chance", "chance-low"

st.divider()

generate = st.button("🚀 Generate Dashboard")

def rank_badge_class(rank):
    if rank == 1:
        return "gold"
    elif rank == 2:
        return "silver"
    elif rank == 3:
        return "bronze"
    return ""

if generate:
    if jd_file and resumes:
        progress_text = st.empty()
        bar = st.progress(0)

        progress_text.text("📄 Reading job description...")
        jd_text = get_text(jd_file)
        jd_keywords = set(word for word in jd_text.split() if len(word) > 4)
        total_keywords = max(len(jd_keywords), 1)
        bar.progress(20)

        results = []
        n = len(resumes)
        for i, res in enumerate(resumes):
            progress_text.text(f"🔍 Analyzing {res.name}...")
            res_text = get_text(res)
            matched = [word for word in jd_keywords if word in res_text]
            missing = [word for word in jd_keywords if word not in res_text]
            score = len(matched)
            pct = round((score / total_keywords) * 100, 1)
            results.append({
                "Candidate": f"{res.name} (#{i+1})" if any(r["Candidate"] == res.name for r in results) or sum(1 for r in resumes if r.name == res.name) > 1 else res.name,
                "Score": score,
                "Match %": pct,
                "Matched Keywords": matched,
                "Missing Keywords": missing,
            })

            # Save result to database
            save_result(res.name, score, pct)

            bar.progress(20 + int(((i + 1) / n) * 80))
            time.sleep(0.1)

        progress_text.empty()
        bar.empty()

        df = pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True)
        df.index += 1

        st.session_state.df = df
        st.session_state.jd_keywords = jd_keywords

        st.success(f"✅ Analysis complete! Ranked {len(df)} candidates.")
    else:
        st.warning("⚠️ Please upload both the Job Description and at least one Resume!")

# Render dashboard if results exist in session state
if st.session_state.df is not None:
        df = st.session_state.df
        jd_keywords = st.session_state.jd_keywords

        # Summary metric cards
        max_score = max(int(df["Score"].max()), 1)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">📁 Total Resumes</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df["Score"].max())}</div><div class="metric-label">🏆 Top Score</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{round(df["Score"].mean(), 1)}</div><div class="metric-label">📊 Average Score</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(jd_keywords)}</div><div class="metric-label">🔑 JD Keywords</div></div>', unsafe_allow_html=True)

        st.write("")
        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(["🏆 Leaderboard", "📋 Candidate Details", "📈 Comparison Graphs", "📥 Export & Summary"])

        # ---------------- TAB 1: LEADERBOARD ----------------
        with tab1:
            st.subheader("Ranked Candidates")

            if len(df) > 0:
                st.markdown(
                    f'<div class="candidate-card" style="border-left:5px solid #ffd200;">'
                    f'🥇 <b>Top Candidate:</b> {df.iloc[0]["Candidate"]} — Score: <b>{df.iloc[0]["Score"]}</b> '
                    f'| Selection Chance: <b>{selection_chance(df.iloc[0]["Match %"])[0]}</b> ({df.iloc[0]["Match %"]}%)'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.write("")

            for rank, row in df.iterrows():
                badge_class = rank_badge_class(rank)
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
                pct = row["Match %"]
                chance_label, chance_class = selection_chance(pct)
                st.markdown(f"""
                    <div class="candidate-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span class="rank-badge {badge_class}">{medal}</span>
                                &nbsp;<b style="color:#222;">{row['Candidate']}</b>
                            </div>
                            <div>
                                <span class="chance-badge {chance_class}">{chance_label} ({pct}%)</span>
                                &nbsp;&nbsp;<b>{row['Score']}</b> pts
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.progress(pct / 100)

        # ---------------- TAB 2: CANDIDATE DETAILS ----------------
        with tab2:
            st.subheader("Explore Individual Candidates")
            selected = st.selectbox("Select a candidate", df["Candidate"], key="candidate_select")
            row = df[df["Candidate"] == selected].iloc[0]
            rank = df[df["Candidate"] == selected].index[0]
            chance_label, chance_class = selection_chance(row["Match %"])

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{int(row["Score"])}</div><div class="metric-label">Match Score</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-value">#{rank}</div><div class="metric-label">Rank</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{row["Match %"]}%</div><div class="metric-label">Selection Chance: {chance_label}</div></div>', unsafe_allow_html=True)

            st.write("")

            # Gauge chart for this candidate's chance
            gauge_color = {"chance-high": "#38ef7d", "chance-medium": "#ffd200", "chance-low": "#ff7043"}[chance_class]
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=row["Match %"],
                title={"text": f"Selection Chance — {selected}"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": gauge_color},
                    "steps": [
                        {"range": [0, 40], "color": "#ffe5e0"},
                        {"range": [40, 70], "color": "#fff6d8"},
                        {"range": [70, 100], "color": "#e2fce9"},
                    ],
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(t=50, b=10, l=30, r=30))
            st.plotly_chart(fig_gauge, use_container_width=True)

            cc1, cc2 = st.columns(2)
            with cc1:
                st.write("**✅ Matched Keywords:**")
                if row["Matched Keywords"]:
                    chips = "".join(
                        f'<span style="display:inline-block; background:#e2fce9; color:#11998e; padding:0.3rem 0.7rem; '
                        f'border-radius:20px; margin:0.2rem; font-size:0.85rem;">{kw}</span>'
                        for kw in row["Matched Keywords"][:30]
                    )
                    st.markdown(chips, unsafe_allow_html=True)
                else:
                    st.write("No keywords matched")

            with cc2:
                st.write("**❌ Missing Keywords:**")
                if row["Missing Keywords"]:
                    chips = "".join(
                        f'<span style="display:inline-block; background:#ffe5e0; color:#e53935; padding:0.3rem 0.7rem; '
                        f'border-radius:20px; margin:0.2rem; font-size:0.85rem;">{kw}</span>'
                        for kw in row["Missing Keywords"][:30]
                    )
                    st.markdown(chips, unsafe_allow_html=True)
                else:
                    st.write("All keywords matched!")

        # ---------------- TAB 3: COMPARISON GRAPHS ----------------
        with tab3:
            st.subheader("📈 Visual Comparison of Candidates")

            # 1. Bar chart - Score comparison
            fig_bar = px.bar(
                df, x="Candidate", y="Score", color="Match %",
                color_continuous_scale=["#ff7043", "#ffd200", "#38ef7d"],
                title="Score Comparison Across Candidates",
                text="Score"
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(height=420)
            st.plotly_chart(fig_bar, use_container_width=True)

            g1, g2 = st.columns(2)

            # 2. Donut chart - Score share
            with g1:
                fig_donut = px.pie(
                    df, names="Candidate", values="Score", hole=0.55,
                    title="Score Share Among Candidates",
                    color_discrete_sequence=px.colors.sequential.Agsunset
                )
                fig_donut.update_traces(textinfo="percent+label")
                fig_donut.update_layout(height=400)
                st.plotly_chart(fig_donut, use_container_width=True)

            # 3. Bar chart - Selection chance %
            with g2:
                fig_chance = px.bar(
                    df, x="Match %", y="Candidate", orientation="h",
                    color="Match %",
                    color_continuous_scale=["#ff7043", "#ffd200", "#38ef7d"],
                    title="Selection Chance (%) per Candidate",
                    text="Match %"
                )
                fig_chance.update_traces(texttemplate="%{text}%", textposition="outside")
                fig_chance.update_layout(height=400, xaxis_range=[0, 100])
                st.plotly_chart(fig_chance, use_container_width=True)

            # 4. Line chart - rank trend
            fig_line = px.line(
                df, x="Candidate", y="Score", markers=True,
                title="Score Trend by Rank Order",
                color_discrete_sequence=["#6a11cb"]
            )
            fig_line.update_layout(height=380)
            st.plotly_chart(fig_line, use_container_width=True)

        # ---------------- TAB 4: EXPORT & FINAL SUMMARY ----------------
        with tab4:
            st.subheader("📊 Final Summary — All Candidates")

            for rank, row in df.iterrows():
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
                badge_class = rank_badge_class(rank)
                chance_label, chance_class = selection_chance(row["Match %"])

                with st.expander(f"{medal} {row['Candidate']} — {row['Score']} pts | {chance_label} ({row['Match %']}%)"):
                    sc1, sc2 = st.columns([1, 2])
                    with sc1:
                        st.markdown(f'<span class="rank-badge {badge_class}">Rank {medal}</span>', unsafe_allow_html=True)
                        st.metric("Match Score", row["Score"])
                        st.metric("Match %", f'{row["Match %"]}%')
                        st.markdown(f'<span class="chance-badge {chance_class}">{chance_label}</span>', unsafe_allow_html=True)
                    with sc2:
                        st.write("**Matched Keywords:**")
                        st.write(", ".join(row["Matched Keywords"][:20]) if row["Matched Keywords"] else "None")
                        st.write("**Missing Keywords:**")
                        st.write(", ".join(row["Missing Keywords"][:20]) if row["Missing Keywords"] else "None")

            st.divider()
            st.subheader("Download Results")

            export_df = df[["Candidate", "Score", "Match %"]].copy()
            export_df["Selection Chance"] = export_df["Match %"].apply(lambda p: selection_chance(p)[0])
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results (CSV)", csv, "results.csv", "text/csv")
            st.dataframe(export_df, use_container_width=True)

elif generate and not (jd_file and resumes):
    st.warning("⚠️ Please upload both the Job Description and at least one Resume!")
else:
    st.info("👆 Upload files and click **Generate Dashboard** to start.")