import streamlit as st
import json
import shutil
import io
from datetime import datetime
from pathlib import Path
import collections

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Studio Archive — Interior Design",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── LIGHT PROFESSIONAL COLOR PALETTE ─────────────────────────────────────────
BG_COLOR = "#f9f7f2"
SIDEBAR_BG = "#f4f1ea"
HERO_GRADIENT = "linear-gradient(135deg, #5c4633 0%, #8c6b5e 50%, #b89e7e 100%)"

PHASES = [
    {"key": "phase1", "label": "Phase 1 — Site Visit & CAD Drafting", "color": "#c97d5f", "icon": "📍"},
    {"key": "phase2", "label": "Phase 2 — Finalising Services & Kitchen", "color": "#5f9b8c", "icon": "🔧"},
    {"key": "phase3", "label": "Phase 3 — 2D & 3D Designs", "color": "#6b5b8c", "icon": "🎨"},
    {"key": "phase4", "label": "Phase 4 — Working Drawings & Selections", "color": "#b89e7e", "icon": "📐"},
]

STATUS_COLORS = {
    "Completed": "#5f9b8c",
    "In Progress": "#c97d5f",
    "Concept / Proposal": "#6b5b8c",
    "On Hold": "#8c7a6b",
}

TYPE_COLORS = ["#c97d5f", "#5f9b8c", "#6b5b8c", "#b89e7e", "#9c6644", "#4a7c6f", "#7a5f9c", "#a88e6f"]

# ─── PATHS ────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
PROJ_FILE = DATA_DIR / "projects.json"
UPLOAD_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# ─── IMPROVED STYLES WITH BETTER TEXT VISIBILITY ──────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{ 
    font-family: 'Inter', sans-serif; 
    color: #2c2c2c !important;
}}

section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
}}
section[data-testid="stSidebar"] * {{ 
    color: #2c2c2c !important; 
}}

.main {{ 
    background: {BG_COLOR}; 
}}

h1, h2, h3, h4, h5, label, .stTextInput label, .stSelectbox label, 
.stTextArea label, .stNumberInput label, .stMultiselect label {{
    color: #2c2c2c !important;
    font-weight: 500;
}}

.hero-header {{
    background: {HERO_GRADIENT};
    color: white; 
    padding: 2.6rem 3rem; 
    border-radius: 24px; 
    margin-bottom: 2.5rem;
}}
.hero-header h1 {{ color: white !important; font-size: 2.7rem; margin:0; }}

.proj-page {{
    background: white; 
    border-radius: 22px; 
    padding: 2.4rem; 
    box-shadow: 0 8px 30px rgba(0,0,0,0.06); 
    margin-bottom: 2.2rem;
    border-top: 8px solid;
}}

.phase-card {{
    border-radius: 18px; 
    padding: 1.4rem 1.6rem; 
    margin-bottom: 1rem;
    border-left: 7px solid; 
    background: white;
    box-shadow: 0 5px 18px rgba(0,0,0,0.05);
}}

.stat-box {{
    border-radius: 20px; 
    padding: 1.8rem 1.2rem; 
    text-align: center; 
    color: white;
    box-shadow: 0 6px 22px rgba(0,0,0,0.07);
}}

.tag {{
    display:inline-block; border-radius:28px; padding:7px 18px;
    font-size:0.83rem; margin:5px; font-weight:500; color:white;
}}

.sidebar-logo {{
    font-family:'Playfair Display',serif; 
    font-size:2.1rem; 
    font-weight:700; 
    color:#2c2c2c; 
    letter-spacing:0.04em;
}}

/* Specific fix for Add New Project form */
.stForm label, .stForm div[data-testid="stMarkdownContainer"] p, 
.stForm .stTextInput > div > div > input, 
.stForm .stTextArea > div > div > textarea {{
    color: #2c2c2c !important;
}}
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def load_projects():
    if PROJ_FILE.exists():
        with open(PROJ_FILE) as f:
            return json.load(f)
    return []

def save_projects(projects):
    with open(PROJ_FILE, "w") as f:
        json.dump(projects, f, indent=2)

def file_icon(name):
    ext = Path(name).suffix.lower()
    m = {".dwg":"📐",".jpg":"🖼️",".png":"🖼️",".pdf":"📄",".mp4":"🎬",".obj":"🧊",".zip":"🗜️",".xlsx":"📊"}
    return m.get(ext, "📎")

def get_thumbnail(proj_dir: Path):
    if proj_dir.exists():
        for ph in PHASES:
            ph_dir = proj_dir / ph["key"]
            if ph_dir.exists():
                for f in ph_dir.iterdir():
                    if f.suffix.lower() in [".jpg",".jpeg",".png",".webp"]:
                        return f
    return None

# Simple exports
def export_excel(proj):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = openpyxl.Workbook()
        ws = wb.active
        ws["A1"] = proj.get("name", "Project")
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()
    except:
        return None

def export_docx(proj):
    try:
        from docx import Document
        doc = Document()
        doc.add_heading(proj.get("name", "Project"), 0)
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.read()
    except:
        return None

def export_html_report(proj):
    return f"<h1>{proj.get('name','Project')}</h1><p>Professional Interior Design Report</p>".encode()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏛️ Studio Archive</div>', unsafe_allow_html=True)
    st.markdown("*Professional Interior Design Portfolio*")
    st.markdown("---")
    page = st.radio("", ["📂 All Projects", "➕ Add New Project", "📊 Statistics"], label_visibility="collapsed")
    st.markdown("---")
    projects = load_projects()
    completed = sum(1 for p in projects if p.get("status") == "Completed")
    active = sum(1 for p in projects if p.get("status") == "In Progress")
    st.markdown(f"**{len(projects)}** total • **{completed}** completed • **{active}** active")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL PROJECTS
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📂 All Projects":
    st.markdown(f"""
    <div class="hero-header">
        <h1>📂 All Projects</h1>
        <p>Your elegant interior design portfolio</p>
    </div>""", unsafe_allow_html=True)

    if not projects:
        st.info("No projects yet. Go to **Add New Project** to begin.")
    else:
        col1, col2, col3, col4 = st.columns([3,2,2,2])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Project name, client...")
        with col2:
            all_types = ["All"] + sorted(set(p.get("project_type","") for p in projects))
            type_filter = st.selectbox("Type", all_types)
        with col3:
            all_years = ["All"] + sorted(set(str(p.get("year","")) for p in projects), reverse=True)
            year_filter = st.selectbox("Year", all_years)
        with col4:
            all_stat = ["All"] + sorted(set(p.get("status","") for p in projects))
            stat_filter = st.selectbox("Status", all_stat)

        filtered = projects[:]
        if search:
            q = search.lower()
            filtered = [p for p in filtered if q in str(p.get("name","")).lower() or q in str(p.get("client","")).lower()]
        if type_filter != "All":
            filtered = [p for p in filtered if p.get("project_type") == type_filter]
        if year_filter != "All":
            filtered = [p for p in filtered if str(p.get("year")) == year_filter]
        if stat_filter != "All":
            filtered = [p for p in filtered if p.get("status") == stat_filter]

        for proj in reversed(filtered):
            proj_dir = UPLOAD_DIR / proj.get("id", "")
            status_color = STATUS_COLORS.get(proj.get("status",""), "#6b5b8c")
            accent = TYPE_COLORS[hash(proj.get("project_type","")) % len(TYPE_COLORS)]
            thumb = get_thumbnail(proj_dir)

            st.markdown(f"""
            <div class="proj-page" style="border-top-color:{accent};">
                <div style="display:flex;justify-content:space-between;align-items:start;">
                    <div>
                        <h2 style="margin:0;">{proj.get('name','Untitled')}</h2>
                        <p style="color:#555;margin:8px 0 0 0;">
                            {proj.get('project_type','—')} • {proj.get('area','—')} • {proj.get('year','—')} • {proj.get('client','—')}
                        </p>
                    </div>
                    <span style="background:{status_color};color:white;padding:6px 20px;border-radius:30px;font-weight:500;">
                        {proj.get('status','—')}
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

            if thumb:
                c1, c2 = st.columns([1, 2.2])
                with c1:
                    st.image(str(thumb), use_container_width=True)
                with c2:
                    st.write(proj.get("description", ""))
            elif proj.get("description"):
                st.write(proj.get("description", ""))

            st.markdown("#### Design Phases")
            ph_cols = st.columns(4)
            for i, ph in enumerate(PHASES):
                ph_dir = proj_dir / ph["key"]
                files = list(ph_dir.iterdir()) if ph_dir.exists() else []
                with ph_cols[i]:
                    file_text = "<br>".join(f"{file_icon(f.name)} {f.name[:22]}" for f in files) if files else "<i style='color:#777'>No files yet</i>"
                    st.markdown(f"""
                    <div class="phase-card" style="border-left-color:{ph['color']};">
                        <strong style="color:{ph['color']};">{ph['icon']} Phase {i+1}</strong><br>
                        <small>{file_text}</small>
                    </div>""", unsafe_allow_html=True)

            st.markdown("**Export Project**")
            e1, e2, e3, d1 = st.columns([2,2,2,1])
            with e1:
                if data := export_excel(proj):
                    st.download_button("📊 Excel", data, f"{proj.get('name','project')}_report.xlsx", use_container_width=True)
            with e2:
                if data := export_docx(proj):
                    st.download_button("📝 Word", data, f"{proj.get('name','project')}_report.docx", use_container_width=True)
            with e3:
                html_data = export_html_report(proj)
                st.download_button("🖨️ HTML Report", html_data, f"{proj.get('name','project')}_report.html", use_container_width=True)
            with d1:
                if st.button("🗑️", key=f"del_{proj.get('id')}"):
                    st.session_state[f"confirm_{proj.get('id')}"] = True

            if st.session_state.get(f"confirm_{proj.get('id')}"):
                st.warning("Delete this project permanently?")
                ya, na = st.columns(2)
                if ya.button("Yes, Delete"):
                    projects = [p for p in projects if p.get("id") != proj.get("id")]
                    save_projects(projects)
                    if proj_dir.exists():
                        shutil.rmtree(proj_dir)
                    st.rerun()
                if na.button("Cancel"):
                    st.session_state[f"confirm_{proj.get('id')}"] = False
                    st.rerun()

            st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD NEW PROJECT (Fixed Text Visibility)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add New Project":
    st.markdown(f"""
    <div class="hero-header">
        <h1>➕ Add New Project</h1>
        <p>Fill in the details and upload files by phase</p>
    </div>""", unsafe_allow_html=True)

    with st.form("add_form", clear_on_submit=True):
        st.subheader("Project Details")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Project Name *", placeholder="e.g. Verma Residence — Living Room")
            client = st.text_input("Client Name")
            year = st.number_input("Year *", min_value=2000, max_value=2030, value=datetime.now().year)
            area = st.text_input("Area / Location", placeholder="e.g. Jubilee Hills, Hyderabad")
        with c2:
            project_type = st.selectbox("Project Type *", ["Residential","Commercial","Office","Hospitality","Retail","Renovation","Other"])
            budget_range = st.selectbox("Budget Range", ["—","Under ₹5L","₹5L–₹20L","₹20L–₹50L","₹50L–₹1Cr","₹1Cr+"])
            status = st.selectbox("Status", ["Completed","In Progress","Concept / Proposal","On Hold"])

        description = st.text_area("Project Description", height=120)
        styles = st.multiselect("Design Styles", ["Contemporary","Modern","Minimalist","Traditional","Luxury","Sustainable","Industrial","Vastu"])

        st.subheader("📁 Upload Files by Phase")
        phase_files = {}
        for ph in PHASES:
            st.markdown(f"**{ph['icon']} {ph['label']}**")
            phase_files[ph["key"]] = st.file_uploader("", accept_multiple_files=True, key=ph["key"])

        notes = st.text_area("Additional Notes")
        submitted = st.form_submit_button("💾 Save Project", use_container_width=True)

    if submitted:
        if not name or not name.strip():
            st.error("Project Name is required!")
        else:
            proj_id = f"{int(datetime.now().timestamp())}_{name[:20].replace(' ','_').lower()}"
            new_proj = {
                "id": proj_id, "name": name.strip(), "client": client,
                "year": int(year), "project_type": project_type, "area": area,
                "budget_range": budget_range, "description": description,
                "styles": styles, "status": status, "notes": notes,
                "created_at": datetime.now().isoformat()
            }

            proj_dir = UPLOAD_DIR / proj_id
            total_files = 0
            for ph in PHASES:
                files = phase_files.get(ph["key"]) or []
                if files:
                    ph_dir = proj_dir / ph["key"]
                    ph_dir.mkdir(parents=True, exist_ok=True)
                    for uf in files:
                        with open(ph_dir / uf.name, "wb") as fh:
                            fh.write(uf.getbuffer())
                        total_files += 1

            projects.append(new_proj)
            save_projects(projects)
            st.success(f"✅ Project **{name}** saved successfully with {total_files} files!")
            st.balloons()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Statistics":
    st.markdown(f"""
    <div class="hero-header">
        <h1>📊 Studio Statistics</h1>
        <p>Overview of your interior design practice</p>
    </div>""", unsafe_allow_html=True)

    if not projects:
        st.info("No projects yet.")
    else:
        total_files = sum(
            sum(len(list((UPLOAD_DIR / p.get("id", "") / ph["key"]).iterdir())) 
                for ph in PHASES if (UPLOAD_DIR / p.get("id", "") / ph["key"]).exists())
            for p in projects
        )

        cols = st.columns(5)
        values = [len(projects), 
                  sum(1 for p in projects if p.get("status") == "Completed"),
                  sum(1 for p in projects if p.get("status") == "In Progress"),
                  total_files,
                  len(set(p.get("year") for p in projects))]
        labels = ["Total Projects", "Completed", "In Progress", "Total Files", "Active Years"]
        colors = ["#6b5b8c", "#5f9b8c", "#c97d5f", "#b89e7e", "#8c6b5e"]

        for col, val, label, color in zip(cols, values, labels, colors):
            with col:
                st.markdown(f"""
                <div class="stat-box" style="background:{color};">
                    <div style="font-size:2.8rem; font-weight:700;">{val}</div>
                    <div style="font-size:0.9rem;">{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        ca, cb = st.columns(2)
        with ca:
            st.subheader("Projects by Type")
            st.bar_chart(dict(collections.Counter(p.get("project_type","Other") for p in projects)))
        with cb:
            st.subheader("Projects by Year")
            st.bar_chart(dict(sorted(collections.Counter(p.get("year") for p in projects).items())))
