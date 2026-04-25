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

# ─── PASTEL COLORS ────────────────────────────────────────────────────────────
PASTEL_BG = "#f8f4f9"
PASTEL_ACCENT = "#d4a5d9"

PHASES = [
    {"key": "phase1", "label": "Phase 1 — Site Visit & CAD Drafting", "color": "#f8a5b8", "icon": "📍"},
    {"key": "phase2", "label": "Phase 2 — Finalising Services & Kitchen", "color": "#f9d38a", "icon": "🔧"},
    {"key": "phase3", "label": "Phase 3 — 2D & 3D Designs", "color": "#a2d2e2", "icon": "🎨"},
    {"key": "phase4", "label": "Phase 4 — Working Drawings & Selections", "color": "#a8e6cf", "icon": "📐"},
]

STATUS_COLORS = {
    "Completed": "#7ed6b3",
    "In Progress": "#f9c96b",
    "Concept / Proposal": "#c4a7e7",
    "On Hold": "#f8a5b8",
}

TYPE_COLORS = ["#f8a5b8", "#f9d38a", "#a2d2e2", "#a8e6cf", "#d4a5d9", "#f9c4a8", "#b8e0d2", "#e6c3f0"]

# ─── PATHS ────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
PROJ_FILE = DATA_DIR / "projects.json"
UPLOAD_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# ─── STYLES (Beautiful Pastel) ────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Nunito:wght@300;400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #e8d9f0 0%, #d4c4e8 100%); }}
section[data-testid="stSidebar"] * {{ color: #4a2c6d !important; }}
.main {{ background: {PASTEL_BG}; }}
h1,h2,h3 {{ font-family: 'Playfair Display', serif !important; color: #4a2c6d; }}
.proj-page {{ background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 8px 25px rgba(0,0,0,0.06); margin-bottom: 2rem; border-top: 7px solid; }}
.phase-card {{ border-radius: 16px; padding: 1.1rem 1.3rem; margin-bottom: 0.8rem; border-left: 6px solid; background: white; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
.stat-box {{ border-radius: 18px; padding: 1.6rem; text-align: center; color: white; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }}
.hero-header {{ background: linear-gradient(135deg, #d4a5d9 0%, #f8c1d4 50%, #a8e6cf 100%); color: white; padding: 2.2rem 2.8rem; border-radius: 22px; margin-bottom: 2rem; }}
.hero-header h1 {{ color: white !important; margin:0; font-size:2.4rem; }}
.tag {{ display:inline-block; border-radius:25px; padding:4px 14px; font-size:0.8rem; margin:3px; font-weight:600; color:white; }}
.sidebar-logo {{ font-family:'Playfair Display',serif; font-size:1.8rem; font-weight:700; color:#4a2c6d; }}
</style>
""", unsafe_allow_html=True)

# ─── HELPERS (same as your original) ──────────────────────────────────────────
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
    m = {".dwg":"📐",".jpg":"🖼️",".png":"🖼️",".pdf":"📄",".mp4":"🎬",".obj":"🧊",".zip":"🗜️", ".xlsx":"📊"}
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

# Export functions (export_excel, export_docx, export_html_report) 
# → Keep your original ones here (they are long, so I didn't repeat them). 
# Just copy-paste your original export functions into this file.

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏛️ Studio Archive</div>', unsafe_allow_html=True)
    st.markdown("*Pastel Interior Design Portfolio*")
    st.markdown("---")
    page = st.radio("", ["📂 All Projects", "➕ Add New Project", "📊 Statistics"], label_visibility="collapsed")
    st.markdown("---")
    projects = load_projects()
    completed_count = sum(1 for p in projects if p.get("status") == "Completed")
    inprog_count = sum(1 for p in projects if p.get("status") == "In Progress")
    st.markdown(f"**{len(projects)}** total • **{completed_count}** completed • **{inprog_count}** active")

# ─── PAGES (All Projects, Add New, Statistics) ───────────────────────────────
# Copy your original page code here (the big blocks for if page == "📂 All Projects", etc.)
# Only change is that colors are now controlled by the new CSS and color dictionaries.

# For brevity, if you want the complete merged code with all pages + exports, reply with "Give full merged code" and I'll provide it in the next message.
