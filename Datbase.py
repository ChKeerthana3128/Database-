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

# ─── LUXURY ELEGANT COLOR PALETTE ─────────────────────────────────────────────
BG_COLOR = "#f9f5ee"
SIDEBAR_BG = "#2c2520"
HERO_GRADIENT = "linear-gradient(135deg, #3f2a1e 0%, #5c4033 45%, #8c6b5e 100%)"

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

# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{ 
    font-family: 'Inter', sans-serif; 
    color: #3f2a1e;
}}

section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
}}
section[data-testid="stSidebar"] * {{ 
    color: #f0e9df !important; 
}}

.main {{ 
    background: {BG_COLOR}; 
}}

h1, h2, h3, h4 {{
    font-family: 'Playfair Display', serif !important; 
    color: #3f2a1e;
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
    box-shadow: 0 10px 32px rgba(0,0,0,0.07); 
    margin-bottom: 2.2rem;
    border-top: 8px solid;
}}

.phase-card {{
    border-radius: 18px; 
    padding: 1.4rem 1.6rem; 
    margin-bottom: 1rem;
    border-left: 7px solid; 
    background: white;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
}}

.stat-box {{
    border-radius: 20px; 
    padding: 1.8rem 1.2rem; 
    text-align: center; 
    color: white;
    box-shadow: 0 8px 25px rgba(0,0,0,0.09);
}}

.tag {{
    display:inline-block; border-radius:28px; padding:7px 18px;
    font-size:0.83rem; margin:5px; font-weight:500; color:white;
}}

.sidebar-logo {{
    font-family:'Playfair Display',serif; 
    font-size:2.1rem; 
    font-weight:700; 
    color:#f0e9df; 
    letter-spacing:0.04em;
}}
</style>
""", unsafe_allow_html=True)

# ─── HELPERS (same as before) ────────────────────────────────────────────────
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

# Export functions (kept simple)
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
    return f"<h1>{proj.get('name','Project')}</h1>".encode()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏛️ Studio Archive</div>', unsafe_allow_html=True)
    st.markdown("*Luxury Interior Design Portfolio*")
    st.markdown("---")
    page = st.radio("", ["📂 All Projects", "➕ Add New Project", "📊 Statistics"], label_visibility="collapsed")
    st.markdown("---")
    projects = load_projects()
    completed = sum(1 for p in projects if p.get("status") == "Completed")
    active = sum(1 for p in projects if p.get("status") == "In Progress")
    st.markdown(f"**{len(projects)}** total • **{completed}** completed • **{active}** active")

# (The rest of the pages — All Projects, Add New Project, Statistics — are the same as my previous full code. 
# If you want me to include the full 400+ lines again with this new palette, just say "include full pages".)

# For now, replace only the color section + style block with the above, and keep your existing page logic.
