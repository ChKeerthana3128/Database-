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

# ─── CONTEMPORARY MODERN COLOR PALETTE ───────────────────────────────────────
BG_COLOR = "#f8f5f0"           # Warm light greige
SIDEBAR_BG = "#1f2a2f"         # Deep charcoal
ACCENT_TERRACOTTA = "#e07a5f"
ACCENT_TEAL = "#2a9d8f"
ACCENT_PLUM = "#6d4c8c"

PHASES = [
    {"key": "phase1", "label": "Phase 1 — Site Visit & CAD Drafting", "color": "#e07a5f", "icon": "📍"},
    {"key": "phase2", "label": "Phase 2 — Finalising Services & Kitchen", "color": "#2a9d8f", "icon": "🔧"},
    {"key": "phase3", "label": "Phase 3 — 2D & 3D Designs", "color": "#6d4c8c", "icon": "🎨"},
    {"key": "phase4", "label": "Phase 4 — Working Drawings & Selections", "color": "#d4b99f", "icon": "📐"},
]

STATUS_COLORS = {
    "Completed": "#2a9d8f",
    "In Progress": "#e07a5f",
    "Concept / Proposal": "#6d4c8c",
    "On Hold": "#8c6b5e",
}

TYPE_COLORS = ["#e07a5f", "#2a9d8f", "#6d4c8c", "#d4b99f", "#9c6644", "#4a7c59", "#7d5a9e", "#b38b6d"]

# ─── PATHS ────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
PROJ_FILE = DATA_DIR / "projects.json"
UPLOAD_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# ─── MODERN STYLES WITH BETTER TEXT VISIBILITY ────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{ 
    font-family: 'Inter', sans-serif; 
}}

section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
}}
section[data-testid="stSidebar"] * {{ 
    color: #e8e3d9 !important; 
}}

.main {{ 
    background: {BG_COLOR}; 
}}

h1, h2, h3, h4, h5, h6, p, span, div, label {{
    color: #1f2a2f !important;
}}

.proj-page {{
    background: white; 
    border-radius: 20px; 
    padding: 2.2rem; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
    margin-bottom: 2.2rem;
    border-top: 8px solid;
}}

.phase-card {{
    border-radius: 16px; 
    padding: 1.2rem 1.4rem; 
    margin-bottom: 1rem;
    border-left: 7px solid; 
    background: white;
    box-shadow: 0 6px 20px rgba(0,0,0,0.07);
}}

.stat-box {{
    border-radius: 18px; 
    padding: 1.8rem 1.2rem; 
    text-align: center; 
    color: white;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}}

.hero-header {{
    background: linear-gradient(135deg, #1f2a2f 0%, #2a3a3f 40%, #6d4c8c 100%);
    color: white; 
    padding: 2.5rem 3rem; 
    border-radius: 24px; 
    margin-bottom: 2.5rem;
}}
.hero-header h1 {{ color: white !important; margin:0; font-size:2.6rem; }}

.tag {{
    display:inline-block; border-radius:25px; padding:5px 15px;
    font-size:0.82rem; margin:4px; font-weight:600; color:white;
}}

.sidebar-logo {{
    font-family:'Playfair Display',serif; 
    font-size:1.95rem; 
    font-weight:700; 
    color:#e8e3d9; 
    letter-spacing:0.04em;
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
    m = {
        ".dwg":"📐",".dxf":"📐",".rvt":"📐",".skp":"📐",
        ".jpg":"🖼️",".jpeg":"🖼️",".png":"🖼️",".webp":"🖼️",
        ".pdf":"📄",".mp4":"🎬",".mov":"🎬",
        ".obj":"🧊",".fbx":"🧊",".blend":"🧊",
        ".xlsx":"📊",".zip":"🗜️"
    }
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

# ─── EXPORT FUNCTIONS (unchanged) ─────────────────────────────────────────────
def export_excel(proj):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Project Summary"
        ws.merge_cells("A1:D1")
        ws["A1"] = proj["name"]
        ws["A1"].font = Font(bold=True, size=16, color="FFFFFF")
        ws["A1"].fill = PatternFill("solid", fgColor="1f2a2f")
        ws["A1"].alignment = Alignment(horizontal="center")
        fields = [
            ("Client", proj.get("client","—")),
            ("Year", str(proj.get("year","—"))),
            ("Project Type", proj.get("project_type","—")),
            ("Area", proj.get("area","—")),
            ("Budget Range", proj.get("budget_range","—")),
            ("Status", proj.get("status","—")),
            ("Design Styles", ", ".join(proj.get("styles",[]))),
            ("Description", proj.get("description","—")),
        ]
        for i, (label, value) in enumerate(fields, start=2):
            ws[f"A{i}"] = label
            ws[f"B{i}"] = str(value)
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None

def export_docx(proj):
    try:
        from docx import Document
        from docx.shared import Pt
        doc = Document()
        doc.add_heading(proj["name"], 0)
        for label, value in [("Client", proj.get("client")), ("Year", proj.get("year")), 
                             ("Type", proj.get("project_type")), ("Status", proj.get("status"))]:
            if value:
                p = doc.add_paragraph()
                p.add_run(f"{label}: ").bold = True
                p.add_run(str(value))
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None

def export_html_report(proj):
    html = f"""<!DOCTYPE html>
<html><head><title>{proj['name']}</title>
<style>body {{font-family:Inter,sans-serif; background:#f8f5f0; padding:40px;}}
h1 {{color:#1f2a2f;}} .phase {{margin:20px 0; padding:15px; border-left:6px solid;}}
</style></head><body>
<h1>{proj['name']}</h1>
<p>Client: {proj.get('client','—')}</p>
<p>Status: {proj.get('status','—')}</p>
<h2>Phases</h2>
{"".join(f"<div class='phase' style='border-color:{ph['color']};'><h3>{ph['icon']} {ph['label']}</h3></div>" for ph in PHASES)}
</body></html>"""
    return html.encode("utf-8")

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏛️ Studio Archive</div>', unsafe_allow_html=True)
    st.markdown("*Contemporary Interior Design Portfolio*")
    st.markdown("---")
    page = st.radio("", ["📂 All Projects", "➕ Add New Project", "📊 Statistics"], label_visibility="collapsed")
    st.markdown("---")
    projects = load_projects()
    completed_count = sum(1 for p in projects if p.get("status") == "Completed")
    inprog_count = sum(1 for p in projects if p.get("status") == "In Progress")
    st.markdown(f"**{len(projects)}** total • **{completed_count}** completed • **{inprog_count}** active")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL PROJECTS
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📂 All Projects":
    st.markdown("""
    <div class="hero-header">
        <h1>📂 All Projects</h1>
        <p>Your complete contemporary interior design portfolio</p>
    </div>""", unsafe_allow_html=True)

    if not projects:
        st.info("No projects yet. Go to **Add New Project** to start.")
    else:
        col1, col2, col3, col4 = st.columns([3,2,2,2])
        with col1:
            search = st.text_input("🔍 Search projects", placeholder="Name, client, or description...")
        with col2:
            types = ["All"] + sorted(set(p.get("project_type","") for p in projects))
            type_filter = st.selectbox("Project Type", types)
        with col3:
            years = ["All"] + sorted(set(str(p.get("year","")) for p in projects), reverse=True)
            year_filter = st.selectbox("Year", years)
        with col4:
            stats = ["All"] + sorted(set(p.get("status","") for p in projects))
            stat_filter = st.selectbox("Status", stats)

        filtered = projects[:]
        if search:
            q = search.lower()
            filtered = [p for p in filtered if q in str(p.get("name","")).lower() or 
                        q in str(p.get("client","")).lower() or 
                        q in str(p.get("description","")).lower()]
        if type_filter != "All":
            filtered = [p for p in filtered if p.get("project_type") == type_filter]
        if year_filter != "All":
            filtered = [p for p in filtered if str(p.get("year")) == year_filter]
        if stat_filter != "All":
            filtered = [p for p in filtered if p.get("status") == stat_filter]

        st.caption(f"Showing **{len(filtered)}** of **{len(projects)}** projects")

        for proj in reversed(filtered):
            proj_dir = UPLOAD_DIR / proj["id"]
            status_color = STATUS_COLORS.get(proj.get("status",""), "#6d4c8c")
            accent = TYPE_COLORS[hash(proj.get("project_type","")) % len(TYPE_COLORS)]
            thumb = get_thumbnail(proj_dir)

            st.markdown(f"""
            <div class="proj-page" style="border-top-color:{accent};">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <h2 style="margin:0;">{proj.get('name','Untitled')}</h2>
                        <p style="color:#555;margin:8px 0 0 0;">
                            {proj.get('project_type','—')} • {proj.get('area','—')} • {proj.get('year','—')} • Client: {proj.get('client','—')}
                        </p>
                    </div>
                    <span style="background:{status_color};color:white;padding:6px 18px;border-radius:30px;font-weight:600;">
                        {proj.get('status','—')}
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

            if thumb:
                c1, c2 = st.columns([1,2])
                with c1:
                    st.image(str(thumb), use_container_width=True)
                with c2:
                    if proj.get("description"):
                        st.write(proj["description"])
            else:
                if proj.get("description"):
                    st.write(proj["description"])

            # Phases
            st.markdown("#### Design Phases")
            ph_cols = st.columns(4)
            for i, ph in enumerate(PHASES):
                ph_dir = proj_dir / ph["key"]
                files = list(ph_dir.iterdir()) if ph_dir.exists() else []
                with ph_cols[i]:
                    file_text = "<br>".join(f"{file_icon(f.name)} {f.name[:25]}" for f in files[:5]) if files else "<i>No files yet</i>"
                    st.markdown(f"""
                    <div class="phase-card" style="border-left-color:{ph['color']};">
                        <b style="color:{ph['color']};">{ph['icon']} {ph['label'].split('—')[0]}</b><br>
                        <small>{file_text}</small>
                    </div>""", unsafe_allow_html=True)

            # Export buttons
            st.markdown("**Export Project**")
            e1, e2, e3, d1 = st.columns([2,2,2,1])
            with e1:
                if excel_data := export_excel(proj):
                    st.download_button("📊 Excel", excel_data, f"{proj['name']}_report.xlsx", use_container_width=True)
            with e2:
                if docx_data := export_docx(proj):
                    st.download_button("📝 Word", docx_data, f"{proj['name']}_report.docx", use_container_width=True)
            with e3:
                html_data = export_html_report(proj)
                st.download_button("🖨️ HTML Report", html_data, f"{proj['name']}_report.html", use_container_width=True)
            with d1:
                if st.button("🗑️", key=f"del_{proj['id']}"):
                    st.session_state[f"confirm_{proj['id']}"] = True

            if st.session_state.get(f"confirm_{proj['id']}"):
                st.warning(f"Delete **{proj.get('name')}** permanently?")
                col_yes, col_no = st.columns(2)
                if col_yes.button("Yes, Delete", key=f"yes_{proj['id']}"):
                    projects = [p for p in projects if p["id"] != proj["id"]]
                    save_projects(projects)
                    if proj_dir.exists():
                        shutil.rmtree(proj_dir)
                    st.rerun()
                if col_no.button("Cancel", key=f"no_{proj['id']}"):
                    st.session_state[f"confirm_{proj['id']}"] = False
                    st.rerun()

            st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD NEW PROJECT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add New Project":
    st.markdown("""
    <div class="hero-header">
        <h1>➕ Add New Project</h1>
        <p>Enter project details and upload files by phase</p>
    </div>""", unsafe_allow_html=True)

    with st.form("add_form", clear_on_submit=True):
        st.subheader("Project Details")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Project Name *", placeholder="e.g. Verma Residence - Living Room")
            client = st.text_input("Client Name")
            year = st.number_input("Year *", min_value=2000, max_value=2030, value=datetime.now().year)
            area = st.text_input("Area / Location", placeholder="e.g. Jubilee Hills, Hyderabad")
        with c2:
            project_type = st.selectbox("Project Type *", ["Residential","Commercial","Office","Hospitality","Retail","Renovation","Other"])
            budget_range = st.selectbox("Budget Range", ["—","Under ₹5L","₹5L–₹20L","₹20L–₹50L","₹50L–₹1Cr","₹1Cr+"])
            status = st.selectbox("Status", ["Completed","In Progress","Concept / Proposal","On Hold"])

        description = st.text_area("Project Description", height=100)
        styles = st.multiselect("Design Styles", ["Contemporary","Modern","Minimalist","Traditional","Luxury","Sustainable","Vastu","Industrial"])

        st.subheader("Upload Files by Phase")
        phase_files = {}
        for ph in PHASES:
            st.markdown(f"**{ph['icon']} {ph['label']}**")
            phase_files[ph["key"]] = st.file_uploader("", accept_multiple_files=True, key=ph["key"])

        notes = st.text_area("Additional Notes")
        submitted = st.form_submit_button("💾 Save Project", use_container_width=True)

    if submitted:
        if not name:
            st.error("Project Name is required!")
        else:
            proj_id = f"{int(datetime.now().timestamp())}_{name[:20].replace(' ','_').lower()}"
            new_proj = {
                "id": proj_id,
                "name": name,
                "client": client,
                "year": int(year),
                "project_type": project_type,
                "area": area,
                "budget_range": budget_range,
                "description": description,
                "styles": styles,
                "status": status,
                "notes": notes,
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
                        with open(ph_dir / uf.name, "wb") as f:
                            f.write(uf.getbuffer())
                        total_files += 1

            projects.append(new_proj)
            save_projects(projects)
            st.success(f"✅ Project **{name}** saved successfully with {total_files} files!")
            st.balloons()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Statistics":
    st.markdown("""
    <div class="hero-header">
        <h1>📊 Studio Statistics</h1>
        <p>Overview of your interior design practice</p>
    </div>""", unsafe_allow_html=True)

    if not projects:
        st.info("No projects yet.")
    else:
        total_files = sum(
            sum(len(list((UPLOAD_DIR / p["id"] / ph["key"]).iterdir())) 
                for ph in PHASES if (UPLOAD_DIR / p["id"] / ph["key"]).exists())
            for p in projects
        )

        cols = st.columns(5)
        values = [len(projects), 
                  sum(1 for p in projects if p.get("status") == "Completed"),
                  sum(1 for p in projects if p.get("status") == "In Progress"),
                  total_files,
                  len(set(p.get("year") for p in projects))]
        labels = ["Total Projects", "Completed", "In Progress", "Total Files", "Active Years"]
        colors = ["#6d4c8c", "#2a9d8f", "#e07a5f", "#d4b99f", "#1f2a2f"]

        for col, val, label, color in zip(cols, values, labels, colors):
            with col:
                st.markdown(f"""
                <div class="stat-box" style="background:{color};">
                    <div style="font-size:2.8rem; font-weight:700;">{val}</div>
                    <div style="font-size:0.9rem; opacity:0.9;">{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        ca, cb = st.columns(2)
        with ca:
            st.subheader("Projects by Type")
            st.bar_chart(dict(collections.Counter(p.get("project_type","Other") for p in projects)))
        with cb:
            st.subheader("Projects by Year")
            st.bar_chart(dict(sorted(collections.Counter(p.get("year") for p in projects).items())))

        st.markdown("---")
        st.subheader("Recent Projects")
        for p in sorted(projects, key=lambda x: x.get("created_at",""), reverse=True)[:6]:
            st.markdown(f"**{p.get('name')}** — {p.get('project_type')} ({p.get('year')})")
