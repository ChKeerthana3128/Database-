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

# ─── CONTEMPORARY COLOR PALETTE 2026 ──────────────────────────────────────────
BG_COLOR = "#f8f5f0"           # Warm greige / light beige (modern neutral)
SIDEBAR_COLOR = "#1f2a2f"      # Deep charcoal-teal
ACCENT_TERRACOTTA = "#e07a5f"
ACCENT_TEAL = "#2a9d8f"
ACCENT_PLUM = "#6d4c8c"
ACCENT_BEIGE = "#d4b99f"

PHASES = [
    {"key": "phase1", "label": "Phase 1 — Site Visit & CAD Drafting", "color": "#e07a5f", "icon": "📍"},   # Terracotta
    {"key": "phase2", "label": "Phase 2 — Finalising Services & Kitchen", "color": "#2a9d8f", "icon": "🔧"}, # Teal
    {"key": "phase3", "label": "Phase 3 — 2D & 3D Designs", "color": "#6d4c8c", "icon": "🎨"},            # Plum
    {"key": "phase4", "label": "Phase 4 — Working Drawings & Selections", "color": "#d4b99f", "icon": "📐"}, # Warm beige
]

STATUS_COLORS = {
    "Completed": "#2a9d8f",      # Teal (fresh & successful)
    "In Progress": "#e07a5f",    # Terracotta (energetic)
    "Concept / Proposal": "#6d4c8c",  # Plum (creative)
    "On Hold": "#8c6b5e",        # Warm muted brown
}

TYPE_COLORS = ["#e07a5f", "#2a9d8f", "#6d4c8c", "#d4b99f", "#9c6644", "#4a7c59", "#7d5a9e", "#b38b6d"]

# ─── PATHS ────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
PROJ_FILE = DATA_DIR / "projects.json"
UPLOAD_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# ─── MODERN STYLES ────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{ 
    font-family: 'Inter', sans-serif; 
}}
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #1f2a2f 0%, #162023 100%);
}}
section[data-testid="stSidebar"] * {{ color: #e8e3d9 !important; }}

.main {{ 
    background: {BG_COLOR}; 
}}

h1, h2, h3 {{ 
    font-family: 'Playfair Display', serif !important; 
    color: #1f2a2f;
    font-weight: 700;
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

# ─── HELPERS (unchanged from your original) ───────────────────────────────────
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
        ".dwg":"📐",".dxf":"📐",".rvt":"📐",".jpg":"🖼️",".png":"🖼️",".pdf":"📄",
        ".mp4":"🎬",".obj":"🧊",".zip":"🗜️",".xlsx":"📊"
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

# Paste your original export_excel, export_docx, export_html_report functions here (they remain unchanged)

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

# ─── Rest of your pages (All Projects, Add New Project, Statistics) ───────────
# Copy-paste the rest of your original code from the "if page == ..." blocks onwards.
# The colors will now automatically apply through the new CSS and color variables.

# If you want me to merge everything into one complete file, just say "Give full complete code".
