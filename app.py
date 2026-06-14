import streamlit as st
import PyPDF2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import init_db, save_analysis

init_db()

if "df" not in st.session_state:
    st.session_state.df = None
if "jd_skills" not in st.session_state:
    st.session_state.jd_skills = None

st.set_page_config(page_title="Resume Analyzer", layout="wide", page_icon="🔍")

# ─────────────────── CLEAN SKILL LIST ────────────────────────────────────────
SKILL_DOMAINS = {
    "Programming":  ["python","java","c++","c#","javascript","typescript","ruby","php","swift","kotlin","go","rust","scala","r","matlab","perl","dart"],
    "Web/Frontend": ["html","css","react","angular","vue","nextjs","tailwind","bootstrap","sass","redux","webpack","figma","jquery","gatsby"],
    "Backend":      ["node","django","flask","fastapi","spring","express","laravel","rails","rest","graphql","api","microservices","grpc"],
    "Data/ML":      ["machine learning","deep learning","nlp","tensorflow","pytorch","keras","scikit-learn","pandas","numpy","data science","llm","bert","gpt","opencv","xgboost","spark"],
    "Cloud/DevOps": ["aws","azure","gcp","docker","kubernetes","terraform","jenkins","ci/cd","devops","linux","bash","git","github","gitlab","ansible"],
    "Databases":    ["sql","mysql","postgresql","mongodb","redis","elasticsearch","oracle","sqlite","dynamodb","cassandra","nosql","firebase"],
    "Soft Skills":  ["communication","leadership","teamwork","problem solving","agile","scrum","project management","analytical","critical thinking","collaboration"],
}

PALETTE = {
    "bg":       "#0d0d1f",
    "card":     "#16163a",
    "card2":    "#1e1e4a",
    "border":   "#6c63ff",
    "accent1":  "#6c63ff",   # purple
    "accent2":  "#f7568a",   # pink
    "accent3":  "#ff8c42",   # orange
    "accent4":  "#00e5ff",   # cyan
    "accent5":  "#a29bfe",   # lavender
    "text":     "#e2e8f0",
    "muted":    "#94a3b8",
}

RADAR_COLORS = ["#6c63ff","#f7568a","#ff8c42","#00e5ff","#a29bfe","#ffd166","#06d6a0","#ef476f"]
RADAR_FILLS  = [
    "rgba(108,99,255,0.15)","rgba(247,86,138,0.15)","rgba(255,140,66,0.15)",
    "rgba(0,229,255,0.15)","rgba(162,155,254,0.15)","rgba(255,209,102,0.15)",
    "rgba(6,214,160,0.15)","rgba(239,71,111,0.15)",
]

def get_text(file):
    reader = PyPDF2.PdfReader(file)
    return " ".join([p.extract_text() or "" for p in reader.pages])

def extract_skills_from_text(text):
    text_lower = text.lower()
    found = {}
    for domain, skills in SKILL_DOMAINS.items():
        matched = [s for s in skills if re.search(r'\b' + re.escape(s) + r'\b', text_lower)]
        found[domain] = matched
    return found

def compute_similarity(jd_text, res_text):
    try:
        vec = TfidfVectorizer(stop_words="english")
        tfidf = vec.fit_transform([jd_text, res_text])
        return round(float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]) * 100, 1)
    except:
        return 0.0

def selection_chance(pct):
    if pct >= 65:   return "High Chance",   "chance-high"
    elif pct >= 35: return "Medium Chance", "chance-medium"
    else:           return "Low Chance",    "chance-low"

def rank_badge_class(rank):
    if rank == 1: return "gold"
    elif rank == 2: return "silver"
    elif rank == 3: return "bronze"
    return ""

# ───────────────────────────── CSS ───────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
*{{box-sizing:border-box;}}
html,body,[class*="css"]{{font-family:'Poppins',sans-serif;}}

.stApp{{background:{PALETTE['bg']};min-height:100vh;}}

.main-header{{
    font-size:5.2rem;font-weight:800;
    background:linear-gradient(270deg,{PALETTE['accent1']},{PALETTE['accent2']},{PALETTE['accent3']},{PALETTE['accent4']});
    background-size:300% auto;
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    text-align:center;padding:1.8rem 0 0.4rem 0;
    animation:fadeInDown 0.8s ease, gradientShift 4s ease infinite;
    letter-spacing:4px;
    filter:drop-shadow(0 0 30px rgba(108,99,255,0.4));
}}
@keyframes gradientShift{{
    0%{{background-position:0% center;}}
    50%{{background-position:100% center;}}
    100%{{background-position:0% center;}}
}}
.sub-header{{
    text-align:center;color:{PALETTE['muted']};
    margin-bottom:1.8rem;font-size:1.2rem;animation:fadeIn 1.2s ease;
}}

@keyframes fadeInDown{{from{{opacity:0;transform:translateY(-20px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes fadeInUp{{from{{opacity:0;transform:translateY(15px)}}to{{opacity:1;transform:translateY(0)}}}}

h1,h2,h3,h4,h5,h6{{color:{PALETTE['text']}!important;}}
label,p,.stMarkdown p{{color:{PALETTE['muted']}!important;}}

/* BUTTON */
.stButton>button{{
    width:100%;
    background:linear-gradient(90deg,{PALETTE['accent1']},{PALETTE['accent2']},{PALETTE['accent3']});
    color:white;font-weight:700;font-size:1.15rem;padding:0.85rem;
    border-radius:14px;border:none;transition:all 0.3s ease;letter-spacing:0.5px;
}}
.stButton>button:hover{{transform:scale(1.02);box-shadow:0 8px 28px rgba(108,99,255,0.5);}}

.stDownloadButton>button{{
    width:100%;background:linear-gradient(90deg,{PALETTE['accent1']},{PALETTE['accent2']});
    color:white;font-weight:600;padding:0.75rem;border-radius:12px;border:none;transition:all 0.3s ease;
}}
.stDownloadButton>button:hover{{transform:scale(1.02);box-shadow:0 6px 18px rgba(247,86,138,0.45);}}

/* METRIC CARD */
.metric-card{{
    background:linear-gradient(135deg,{PALETTE['card']},{PALETTE['card2']});
    padding:1.6rem;border-radius:18px;text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,0.5);
    transition:transform 0.25s ease,box-shadow 0.25s ease;
    animation:fadeInUp 0.6s ease;
    border:1px solid rgba(108,99,255,0.35);
}}
.metric-card:hover{{transform:translateY(-7px);box-shadow:0 12px 32px rgba(108,99,255,0.4);}}
.metric-value{{
    font-size:2.6rem;font-weight:800;
    background:linear-gradient(90deg,{PALETTE['accent4']},{PALETTE['accent1']},{PALETTE['accent2']});
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}}
.metric-label{{font-size:0.95rem;color:{PALETTE['muted']};margin-top:0.3rem;}}

/* CANDIDATE CARD */
.candidate-card{{
    background:linear-gradient(135deg,{PALETTE['card']},{PALETTE['card2']});
    border-radius:16px;padding:1.2rem 1.6rem;margin-bottom:0.9rem;
    box-shadow:0 3px 14px rgba(0,0,0,0.35);border-left:5px solid {PALETTE['accent1']};
    transition:transform 0.25s ease,box-shadow 0.25s ease;animation:fadeInUp 0.5s ease;
}}
.candidate-card:hover{{transform:translateX(7px) scale(1.01);box-shadow:0 8px 28px rgba(108,99,255,0.45);border-left-color:{PALETTE['accent2']};}}

.candidate-name{{
    font-size:1.5rem;font-weight:700;color:{PALETTE['text']};
    transition:color 0.3s ease;
}}
.candidate-card:hover .candidate-name{{color:{PALETTE['accent4']};}}
.candidate-name{{font-size:1.35rem;font-weight:700;color:{PALETTE['text']};}}

/* BADGES */
.rank-badge{{display:inline-block;padding:0.28rem 0.85rem;border-radius:20px;font-weight:700;font-size:0.85rem;color:white;background:linear-gradient(90deg,{PALETTE['accent1']},{PALETTE['accent2']});}}
.gold{{background:linear-gradient(90deg,#ff8c42,#ffd166)!important;color:#1a1a1a!important;}}
.silver{{background:linear-gradient(90deg,#94a3b8,#cbd5e1)!important;color:#1a1a1a!important;}}
.bronze{{background:linear-gradient(90deg,#b45309,#d97706)!important;color:#fff!important;}}

.chance-badge{{display:inline-block;padding:0.28rem 0.9rem;border-radius:20px;font-weight:700;font-size:0.85rem;}}
.chance-high{{background:linear-gradient(90deg,#06d6a0,#00e5ff);color:#012a1a!important;}}
.chance-medium{{background:linear-gradient(90deg,#ff8c42,#ffd166);color:#2a1500!important;}}
.chance-low{{background:linear-gradient(90deg,#ef476f,#f7568a);color:#fff!important;}}

/* SKILL CHIPS */
.skill-chip-match{{
    display:inline-block;
    background:linear-gradient(90deg,#0a3d2e,#06d6a0);
    color:#d1fae5;padding:0.35rem 0.85rem;border-radius:25px;
    margin:0.25rem;font-size:0.88rem;font-weight:600;
    border:1px solid rgba(6,214,160,0.4);
    transition:transform 0.2s ease;
}}
.skill-chip-miss{{
    display:inline-block;
    background:linear-gradient(90deg,#4a0a1a,#ef476f);
    color:#fee2e2;padding:0.35rem 0.85rem;border-radius:25px;
    margin:0.25rem;font-size:0.88rem;font-weight:600;
    border:1px solid rgba(239,71,111,0.4);
    transition:transform 0.2s ease;
}}

/* TABS */
div[data-testid="stTabs"] button{{transition:all 0.25s ease;border-radius:8px 8px 0 0;color:{PALETTE['muted']}!important;font-weight:500;}}
div[data-testid="stTabs"] button:hover{{background-color:rgba(108,99,255,0.15);color:{PALETTE['text']}!important;}}
div[data-testid="stTabs"] button[aria-selected="true"]{{background:linear-gradient(90deg,{PALETTE['accent1']},{PALETTE['accent2']})!important;color:#fff!important;font-weight:700;}}

/* FILE UPLOADER */
section[data-testid="stFileUploaderDropzone"]{{background-color:rgba(108,99,255,0.06);border:1.5px dashed {PALETTE['accent1']};border-radius:12px;}}
.stSelectbox label,.stFileUploader label{{color:{PALETTE['text']}!important;font-weight:500;font-size:1rem;}}

/* MISC */
hr{{border-color:rgba(108,99,255,0.2)!important;}}
.section-title{{font-size:1.1rem;font-weight:600;color:{PALETTE['accent4']};margin-bottom:0.5rem;}}
</style>
""", unsafe_allow_html=True)

# ─────────────────── HEADER ──────────────────────────────────────────────────
st.markdown('<p class="main-header">🔍 Resume Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload JD & Resumes — Smart skill matching, radar charts & AI-powered ranking ✨</p>', unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    jd_file = st.file_uploader("📄 Upload Job Description (PDF)", type="pdf")
with col2:
    resumes = st.file_uploader("👥 Upload Resumes (PDFs)", type="pdf", accept_multiple_files=True)

st.divider()
generate = st.button("🚀 Analyze Resumes")

# ─────────────────── ANALYSIS ────────────────────────────────────────────────
if generate:
    if jd_file and resumes:
        progress_text = st.empty()
        bar = st.progress(0)

        progress_text.text("📄 Extracting skills from Job Description...")
        jd_text   = get_text(jd_file)
        jd_skills = extract_skills_from_text(jd_text)
        # All unique skills the JD requires
        jd_all_skills = list({s for skills in jd_skills.values() for s in skills})
        bar.progress(15)

        results = []
        n = len(resumes)
        for i, res in enumerate(resumes):
            progress_text.text(f"🔍 Analyzing {res.name}...")
            res_text   = get_text(res)
            res_skills = extract_skills_from_text(res_text)
            res_all    = {s for skills in res_skills.values() for s in skills}

            # Pure skill match
            matched_skills = sorted([s for s in jd_all_skills if s in res_all])
            missing_skills = sorted([s for s in jd_all_skills if s not in res_all])

            # Domain % match
            domain_scores = {}
            for domain in SKILL_DOMAINS:
                jd_d  = set(jd_skills.get(domain, []))
                res_d = set(res_skills.get(domain, []))
                if jd_d:
                    domain_scores[domain] = round(len(jd_d & res_d) / len(jd_d) * 100, 1)
                else:
                    domain_scores[domain] = 0.0

            # Overall similarity
            overall_pct = compute_similarity(jd_text, res_text)
            skill_pct   = round(len(matched_skills) / max(len(jd_all_skills), 1) * 100, 1) if jd_all_skills else 0.0

            cand_name = (f"{res.name} (#{i+1})"
                         if sum(1 for r in resumes if r.name == res.name) > 1
                         else res.name)

            results.append({
                "Candidate":      cand_name,
                "Skill Match %":  skill_pct,
                "Overall Match %":overall_pct,
                "Domain Scores":  domain_scores,
                "Matched Skills": matched_skills,
                "Missing Skills": missing_skills,
            })

            save_analysis(res.name, len(matched_skills), skill_pct)
            bar.progress(15 + int(((i + 1) / n) * 85))
            time.sleep(0.05)

        progress_text.empty()
        bar.empty()

        df = pd.DataFrame(results).sort_values(by="Skill Match %", ascending=False).reset_index(drop=True)
        df.index += 1
        st.session_state.df        = df
        st.session_state.jd_skills = jd_skills
        st.success(f"✅ Done! Ranked {len(df)} candidates by skill match.")
    else:
        st.warning("⚠️ Please upload both the Job Description and at least one Resume!")

# ─────────────────── DASHBOARD ───────────────────────────────────────────────
if st.session_state.df is not None:
    df        = st.session_state.df
    jd_skills = st.session_state.jd_skills
    jd_all    = sorted({s for v in jd_skills.values() for s in v})

    CHART_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(13,13,31,0.8)",
        font={"color":PALETTE['text'],"family":"Poppins"},
        title_font={"color":PALETTE['text'],"size":16},
        legend=dict(
            bgcolor="rgba(22,22,58,0.95)",
            bordercolor="rgba(108,99,255,0.5)",
            borderwidth=1,
            font=dict(color=PALETTE['text'],size=12)
        ),
    )

    # ── METRIC CARDS ────────────────────────────────────────────────────────
    m1,m2,m3,m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">📁 Candidates</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="metric-value">{df["Skill Match %"].max()}%</div><div class="metric-label">🏆 Best Match</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="metric-value">{round(df["Skill Match %"].mean(),1)}%</div><div class="metric-label">📊 Avg Match</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(jd_all)}</div><div class="metric-label">🔑 Skills in JD</div></div>', unsafe_allow_html=True)

    st.write(""); st.divider()

    tab1,tab2,tab3,tab4 = st.tabs(["🏆 Leaderboard","📋 Candidate Details","📈 Graphs","📥 Export & Summary"])

    # ── TAB 1 ───────────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Ranked Candidates")
        # Show JD skills list at top
        if jd_all:
            st.markdown('<p class="section-title">📋 Skills Required by JD:</p>', unsafe_allow_html=True)
            chips = "".join(f'<span style="display:inline-block;background:rgba(108,99,255,0.25);color:{PALETTE["accent5"]};padding:0.28rem 0.75rem;border-radius:20px;margin:0.2rem;font-size:0.83rem;font-weight:600;border:1px solid rgba(108,99,255,0.4);">{s}</span>' for s in jd_all)
            st.markdown(chips, unsafe_allow_html=True)
            st.write("")

        for rank, row in df.iterrows():
            badge_class   = rank_badge_class(rank)
            medal         = {1:"🥇",2:"🥈",3:"🥉"}.get(rank, f"#{rank}")
            pct           = row["Skill Match %"]
            chance_label, chance_class = selection_chance(pct)
            color         = RADAR_COLORS[(rank-1) % len(RADAR_COLORS)]
            m_count       = len(row["Matched Skills"])
            x_count       = len(row["Missing Skills"])
            st.markdown(f"""
                <div class="candidate-card" style="border-left:5px solid {color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                        <div>
                            <span class="rank-badge {badge_class}">{medal}</span>
                            &nbsp;<span class="candidate-name">{row['Candidate']}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
                            <span style="color:#06d6a0;font-size:0.95rem;font-weight:600;">✅ {m_count} matched</span>
                            <span style="color:#ef476f;font-size:0.95rem;font-weight:600;">❌ {x_count} missing</span>
                            <span class="chance-badge {chance_class}">{chance_label}</span>
                            <b style="color:{PALETTE['accent4']};font-size:1.25rem;">{pct}%</b>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.progress(pct / 100)

    # ── TAB 2 ───────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Explore Individual Candidates")
        selected = st.selectbox("Select a candidate", df["Candidate"], key="candidate_select")
        row  = df[df["Candidate"] == selected].iloc[0]
        rank = df[df["Candidate"] == selected].index[0]
        chance_label, chance_class = selection_chance(row["Skill Match %"])

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">{row["Skill Match %"]}%</div><div class="metric-label">🎯 Skill Match</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">#{rank}</div><div class="metric-label">🏆 Rank</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(row["Matched Skills"])}</div><div class="metric-label">✅ Skills Found</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(row["Missing Skills"])}</div><div class="metric-label">❌ Skills Missing</div></div>', unsafe_allow_html=True)

        st.write("")

        # Gauge
        gauge_color = {"chance-high":"#06d6a0","chance-medium":"#ff8c42","chance-low":"#ef476f"}[chance_class]
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=row["Skill Match %"],
            title={"text":f"Skill Match — {selected}","font":{"color":PALETTE['text'],"size":14}},
            number={"font":{"color":PALETTE['accent4'],"size":48},"suffix":"%"},
            gauge={
                "axis":{"range":[0,100],"tickcolor":PALETTE['muted'],"tickfont":{"color":PALETTE['muted']}},
                "bar":{"color":gauge_color,"thickness":0.25},
                "bgcolor":"rgba(0,0,0,0)",
                "borderwidth":0,
                "steps":[
                    {"range":[0,35],  "color":"rgba(239,71,111,0.15)"},
                    {"range":[35,65], "color":"rgba(255,140,66,0.15)"},
                    {"range":[65,100],"color":"rgba(6,214,160,0.15)"},
                ],
                "threshold":{"line":{"color":PALETTE['accent2'],"width":3},"thickness":0.8,"value":row["Skill Match %"]}
            }
        ))
        fig_gauge.update_layout(height=320,margin=dict(t=70,b=10,l=30,r=30),**CHART_LAYOUT)
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Domain bar
        domain_scores = row["Domain Scores"]
        active_domains = {d:v for d,v in domain_scores.items() if v > 0 or any(jd_skills.get(d))}
        if active_domains:
            fig_domain = go.Figure(go.Bar(
                x=list(active_domains.keys()),
                y=list(active_domains.values()),
                marker=dict(
                    color=list(active_domains.values()),
                    colorscale=[[0,PALETTE['accent1']],[0.5,PALETTE['accent2']],[1,PALETTE['accent3']]],
                    showscale=False, line=dict(width=0)
                ),
                text=[f"{v}%" for v in active_domains.values()],
                textposition="outside",
                textfont=dict(color=PALETTE['text'],size=12)
            ))
            fig_domain.update_layout(
                title="Skill Domain Breakdown",
                yaxis=dict(range=[0,120],gridcolor="rgba(108,99,255,0.15)"),
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                height=360,**CHART_LAYOUT
            )
            st.plotly_chart(fig_domain, use_container_width=True)

        st.write("")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(f'<p class="section-title">✅ Matched Skills ({len(row["Matched Skills"])})</p>', unsafe_allow_html=True)
            if row["Matched Skills"]:
                chips = "".join(f'<span class="skill-chip-match">{s}</span>' for s in row["Matched Skills"])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#ef476f;">No skills matched from JD</span>', unsafe_allow_html=True)

        with cc2:
            st.markdown(f'<p class="section-title">❌ Missing Skills ({len(row["Missing Skills"])})</p>', unsafe_allow_html=True)
            if row["Missing Skills"]:
                chips = "".join(f'<span class="skill-chip-miss">{s}</span>' for s in row["Missing Skills"])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#06d6a0;font-weight:600;">All JD skills matched! 🎉</span>', unsafe_allow_html=True)

    # ── TAB 3 ───────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("📈 Visual Comparison")

        # RADAR
        st.markdown("#### 🕸️ Skill Domain Radar — All Candidates")
        domains = list(SKILL_DOMAINS.keys())

        fig_radar = go.Figure()
        for i, (rank, row) in enumerate(df.iterrows()):
            color  = RADAR_COLORS[i % len(RADAR_COLORS)]
            fill   = RADAR_FILLS[i % len(RADAR_FILLS)]
            vals   = [row["Domain Scores"].get(d, 0) for d in domains]
            vals_c = vals + [vals[0]]
            cats_c = domains + [domains[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_c, theta=cats_c,
                fill='toself', name=row["Candidate"],
                line=dict(color=color, width=2.5),
                fillcolor=fill,
                marker=dict(color=color, size=8)
            ))

        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(13,13,31,0.9)",
                radialaxis=dict(
                    visible=True, range=[0,100],
                    tickfont=dict(color=PALETTE['muted'],size=10),
                    gridcolor="rgba(108,99,255,0.2)",
                    ticksuffix="%", tickcolor=PALETTE['muted']
                ),
                angularaxis=dict(
                    tickfont=dict(color=PALETTE['text'],size=12),
                    gridcolor="rgba(108,99,255,0.2)"
                ),
            ),
            showlegend=True,
            legend=dict(
                bgcolor="rgba(22,22,58,0.97)",
                bordercolor="rgba(108,99,255,0.5)",
                borderwidth=1,
                font=dict(color=PALETTE['text'],size=13),
                x=1.05, y=1,
                title=dict(text="👤 Candidates",font=dict(color=PALETTE['accent4'],size=13))
            ),
            height=580,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,13,31,0.8)",
            font={"color":PALETTE['text'],"family":"Poppins"},
            title_font={"color":PALETTE['text'],"size":16},
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.divider()

        # Bar — skill match %
        fig_bar = px.bar(
            df, x="Candidate", y="Skill Match %",
            color="Skill Match %",
            color_continuous_scale=[[0,PALETTE['accent1']],[0.5,PALETTE['accent2']],[1,PALETTE['accent3']]],
            title="Skill Match % — All Candidates", text="Skill Match %"
        )
        fig_bar.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
        fig_bar.update_layout(height=420, yaxis=dict(range=[0,115], gridcolor="rgba(108,99,255,0.15)"), **CHART_LAYOUT)
        st.plotly_chart(fig_bar, use_container_width=True)

        g1, g2 = st.columns(2)

        with g1:
            fig_donut = px.pie(
                df, names="Candidate", values="Skill Match %", hole=0.58,
                title="Skill Share",
                color_discrete_sequence=RADAR_COLORS
            )
            fig_donut.update_traces(textinfo="percent+label", textfont_color=PALETTE['text'])
            fig_donut.update_layout(height=420, **CHART_LAYOUT)
            st.plotly_chart(fig_donut, use_container_width=True)

        with g2:
            # Grouped bar: matched vs missing per candidate
            bar_data = pd.DataFrame({
                "Candidate":    df["Candidate"],
                "Matched":      df["Matched Skills"].apply(len),
                "Missing":      df["Missing Skills"].apply(len),
            })
            fig_group = go.Figure()
            fig_group.add_trace(go.Bar(name="✅ Matched", x=bar_data["Candidate"], y=bar_data["Matched"],
                                        marker_color=PALETTE['accent4'], marker_line_width=0))
            fig_group.add_trace(go.Bar(name="❌ Missing", x=bar_data["Candidate"], y=bar_data["Missing"],
                                        marker_color=PALETTE['accent2'], marker_line_width=0))
            fig_group.update_layout(
                barmode="group", title="Matched vs Missing Skills",
                yaxis=dict(gridcolor="rgba(108,99,255,0.15)"),
                height=420, **CHART_LAYOUT
            )
            st.plotly_chart(fig_group, use_container_width=True)

        # Line
        fig_line = px.line(
            df, x="Candidate", y="Skill Match %", markers=True,
            title="Skill Match % Trend",
            color_discrete_sequence=[PALETTE['accent2']]
        )
        fig_line.update_traces(
            line=dict(width=3),
            marker=dict(size=11, color=PALETTE['accent4'], line=dict(color=PALETTE['accent2'],width=2))
        )
        fig_line.update_layout(height=380, yaxis=dict(gridcolor="rgba(108,99,255,0.15)"), **CHART_LAYOUT)
        st.plotly_chart(fig_line, use_container_width=True)

    # ── TAB 4 ───────────────────────────────────────────────────────────────
    with tab4:
        st.subheader("📊 Final Summary — All Candidates")

        for rank, row in df.iterrows():
            medal        = {1:"🥇",2:"🥈",3:"🥉"}.get(rank, f"#{rank}")
            badge_class  = rank_badge_class(rank)
            chance_label, chance_class = selection_chance(row["Skill Match %"])

            with st.expander(f"{medal}  {row['Candidate']}  —  {row['Skill Match %']}% skill match  |  {chance_label}"):
                sc1, sc2 = st.columns([1,2])
                with sc1:
                    st.markdown(f'<span class="rank-badge {badge_class}">Rank {medal}</span><br><br>', unsafe_allow_html=True)
                    st.metric("Skill Match", f'{row["Skill Match %"]}%')
                    st.metric("Overall Similarity", f'{row["Overall Match %"]}%')
                    st.metric("Matched / Total", f'{len(row["Matched Skills"])} / {len(jd_all)}')
                    st.markdown(f'<br><span class="chance-badge {chance_class}">{chance_label}</span>', unsafe_allow_html=True)
                with sc2:
                    st.markdown(f'<p class="section-title">✅ Matched Skills ({len(row["Matched Skills"])})</p>', unsafe_allow_html=True)
                    matched_html = "".join(f'<span class="skill-chip-match">{s}</span>' for s in row["Matched Skills"]) or "None"
                    st.markdown(matched_html, unsafe_allow_html=True)
                    st.write("")
                    st.markdown(f'<p class="section-title">❌ Missing Skills ({len(row["Missing Skills"])})</p>', unsafe_allow_html=True)
                    missing_html = "".join(f'<span class="skill-chip-miss">{s}</span>' for s in row["Missing Skills"]) or "All matched 🎉"
                    st.markdown(missing_html, unsafe_allow_html=True)
                    st.write("")
                    st.markdown('<p class="section-title">📊 Domain Scores</p>', unsafe_allow_html=True)
                    for domain, score in row["Domain Scores"].items():
                        if jd_skills.get(domain):
                            color_d = "#06d6a0" if score >= 65 else "#ff8c42" if score >= 35 else "#ef476f"
                            st.markdown(f'<span style="color:{PALETTE["muted"]};">{domain}:</span> <b style="color:{color_d};">{score}%</b>', unsafe_allow_html=True)

        st.divider()
        st.subheader("⬇️ Download Results")
        export_df = df[["Candidate","Skill Match %","Overall Match %"]].copy()
        export_df["Matched Skills"] = df["Matched Skills"].apply(lambda x: ", ".join(x))
        export_df["Missing Skills"] = df["Missing Skills"].apply(lambda x: ", ".join(x))
        export_df["Selection Chance"] = export_df["Skill Match %"].apply(lambda p: selection_chance(p)[0])
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "results.csv", "text/csv")
        st.dataframe(export_df, use_container_width=True)

elif generate and not (jd_file and resumes):
    st.warning("⚠️ Please upload both the Job Description and at least one Resume!")
else:
    st.info("👆 Upload files and click **Analyze Resumes** to start.")