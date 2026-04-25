import streamlit as st
import json
import os
import shutil
import io
from datetime import datetime
from pathlib import Path
import base64
import collections

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Studio Archive — Interior Design",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── PATHS ────────────────────────────────────────────────────────────────────
DATA_DIR   = Path("data")
PROJ_FILE  = DATA_DIR / "projects.json"
UPLOAD_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# ─── DESIGN PHASES ────────────────────────────────────────────────────────────
PHASES = [
    {"key": "phase1", "label": "Phase 1 — Site Visit & CAD Drafting",       "color": "#FF6B6B", "icon": "📍"},
    {"key": "phase2", "label": "Phase 2 — Finalising Services & Kitchen",    "color": "#F7B731", "icon": "🔧"},
    {"key": "phase3", "label": "Phase 3 — 2D & 3D Designs",                 "color": "#45B7D1", "icon": "🎨"},
    {"key": "phase4", "label": "Phase 4 — Working Drawings & Selections",    "color": "#96CEB4", "icon": "📐"},
]

STATUS_COLORS = {
    "Completed":        "#10b981",
    "In Progress":      "#f59e0b",
    "Concept / Proposal": "#6366f1",
    "On Hold":          "#ef4444",
}

TYPE_COLORS = ["#FF6B6B","#F7B731","#45B7D1","#96CEB4","#A29BFE","#FD79A8","#74B9FF","#00CEC9"]

# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Nunito:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1035 0%, #2d1b69 50%, #1a3a4a 100%);
}
section[data-testid="stSidebar"] * { color: #f0f0f0 !important; }
.main { background: #f8f6ff; }
h1,h2,h3 { font-family: 'Playfair Display', serif !important; }
.phase-card {
    border-radius: 12px; padding: 0.9rem 1.1rem; margin-bottom: 0.5rem;
    border-left: 5px solid; background: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}
.proj-page {
    background: white; border-radius: 18px; padding: 2rem;
    box-shadow: 0 6px 30px rgba(0,0,0,0.10); margin-bottom: 2rem;
    border-top: 6px solid;
}
.stat-box {
    border-radius: 14px; padding: 1.4rem; text-align: center; color: white;
}
.stat-num { font-family:'Playfair Display',serif; font-size:2.8rem; font-weight:700; }
.stat-label { font-size:0.75rem; letter-spacing:0.12em; text-transform:uppercase; opacity:0.85; }
.tag {
    display:inline-block; border-radius:20px; padding:3px 12px;
    font-size:0.78rem; margin:2px; font-weight:700; color:white;
}
.file-chip {
    background:#f3f0ff; border:1px solid #c4b5fd; border-radius:8px;
    padding:4px 11px; font-size:0.78rem; color:#5b21b6; margin:3px;
    display:inline-block; font-weight:600;
}
.divider { border:none; border-top:2px solid #ede9fe; margin:1.5rem 0; }
.hero-header {
    background: linear-gradient(135deg,#667eea 0%,#764ba2 40%,#f64f59 100%);
    color:white; padding:2rem 2.5rem; border-radius:18px; margin-bottom:2rem;
}
.hero-header h1 { color:white !important; margin:0; font-size:2.2rem; }
.hero-header p { opacity:0.9; margin:0.3rem 0 0; font-size:1rem; }
.sidebar-logo {
    font-family:'Playfair Display',serif; font-size:1.5rem;
    font-weight:700; color:white; letter-spacing:0.05em;
}
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
        ".dwg":"📐",".dxf":"📐",".rvt":"📐",".skp":"📐",".dwf":"📐",
        ".jpg":"🖼️",".jpeg":"🖼️",".png":"🖼️",".gif":"🖼️",".webp":"🖼️",
        ".pdf":"📄",".mp4":"🎬",".mov":"🎬",".avi":"🎬",".mkv":"🎬",
        ".obj":"🧊",".fbx":"🧊",".3ds":"🧊",".blend":"🧊",".stl":"🧊",
        ".xlsx":"📊",".csv":"📊",".xls":"📊",".pptx":"📊",
        ".zip":"🗜️",".rar":"🗜️",".7z":"🗜️",
        ".max":"🖥️",".c4d":"🖥️",
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

# ─── EXPORT: EXCEL ────────────────────────────────────────────────────────────
def export_excel(proj):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Project Summary"

        ws.merge_cells("A1:D1")
        ws["A1"] = proj["name"]
        ws["A1"].font = Font(bold=True, size=16, color="FFFFFF")
        ws["A1"].fill = PatternFill("solid", fgColor="5b21b6")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 36

        thin = Border(
            left=Side(style="thin", color="DDD6FE"),
            right=Side(style="thin", color="DDD6FE"),
            top=Side(style="thin", color="DDD6FE"),
            bottom=Side(style="thin", color="DDD6FE"),
        )
        fields = [
            ("Client",        proj.get("client","—")),
            ("Year",          str(proj.get("year","—"))),
            ("Project Type",  proj.get("project_type","—")),
            ("Area",          proj.get("area","—")),
            ("Budget Range",  proj.get("budget_range","—")),
            ("Status",        proj.get("status","—")),
            ("Design Styles", ", ".join(proj.get("styles",[]))),
            ("Description",   proj.get("description","—")),
            ("Notes",         proj.get("notes","—")),
            ("Created",       proj.get("created_at","—")[:10] if proj.get("created_at") else "—"),
        ]
        for i, (label, value) in enumerate(fields, start=2):
            ws[f"A{i}"] = label
            ws[f"A{i}"].font = Font(bold=True, color="5b21b6")
            ws[f"A{i}"].fill = PatternFill("solid", fgColor="EDE9FE")
            ws[f"A{i}"].border = thin
            ws.merge_cells(f"B{i}:D{i}")
            ws[f"B{i}"] = str(value)
            ws[f"B{i}"].border = thin
            ws[f"B{i}"].alignment = Alignment(wrap_text=True)

        row = len(fields) + 3
        proj_dir = UPLOAD_DIR / proj["id"]
        for ph in PHASES:
            ws[f"A{row}"] = ph["icon"] + " " + ph["label"]
            ws[f"A{row}"].font = Font(bold=True, size=11, color="FFFFFF")
            fill_color = ph["color"].lstrip("#")
            ws[f"A{row}"].fill = PatternFill("solid", fgColor=fill_color)
            ws.merge_cells(f"A{row}:D{row}")
            ws[f"A{row}"].alignment = Alignment(horizontal="left")
            row += 1
            ph_dir = proj_dir / ph["key"]
            if ph_dir.exists():
                files = list(ph_dir.iterdir())
                if files:
                    for f in files:
                        ws[f"B{row}"] = f.name
                        ws[f"B{row}"].border = thin
                        row += 1
                else:
                    ws[f"B{row}"] = "No files uploaded"
                    row += 1
            else:
                ws[f"B{row}"] = "No files uploaded"
                row += 1
            row += 1

        ws.column_dimensions["A"].width = 28
        ws.column_dimensions["B"].width = 42
        ws.column_dimensions["C"].width = 18
        ws.column_dimensions["D"].width = 18

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None

# ─── EXPORT: WORD ─────────────────────────────────────────────────────────────
def export_docx(proj):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()
        title = doc.add_heading(proj["name"], 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if title.runs:
            title.runs[0].font.color.rgb = RGBColor(0x5b, 0x21, 0xb6)

        doc.add_paragraph(f"Project Report  |  Generated {datetime.now().strftime('%d %B %Y')}\n")

        doc.add_heading("Project Details", level=1)
        table = doc.add_table(rows=1, cols=2)
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        hdr[0].text = "Field"
        hdr[1].text = "Details"
        for cell in hdr:
            if cell.paragraphs[0].runs:
                cell.paragraphs[0].runs[0].bold = True

        for label, value in [
            ("Client",        proj.get("client","—")),
            ("Year",          str(proj.get("year","—"))),
            ("Project Type",  proj.get("project_type","—")),
            ("Area",          proj.get("area","—")),
            ("Budget Range",  proj.get("budget_range","—")),
            ("Status",        proj.get("status","—")),
            ("Design Styles", ", ".join(proj.get("styles",[]))),
        ]:
            r = table.add_row().cells
            r[0].text = label
            r[1].text = str(value)

        if proj.get("description"):
            doc.add_paragraph()
            doc.add_heading("Project Description", level=1)
            doc.add_paragraph(proj["description"])

        if proj.get("notes"):
            doc.add_heading("Notes", level=1)
            doc.add_paragraph(proj["notes"])

        doc.add_heading("Design Phases & Files", level=1)
        proj_dir = UPLOAD_DIR / proj["id"]
        for ph in PHASES:
            doc.add_heading(ph["icon"] + " " + ph["label"], level=2)
            ph_dir = proj_dir / ph["key"]
            if ph_dir.exists():
                files = list(ph_dir.iterdir())
                if files:
                    for f in files:
                        doc.add_paragraph(f"• {f.name}", style="List Bullet")
                else:
                    doc.add_paragraph("No files uploaded for this phase.")
            else:
                doc.add_paragraph("No files uploaded for this phase.")

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None

# ─── EXPORT: HTML REPORT (print-to-PDF ready) ────────────────────────────────
def export_html_report(proj):
    proj_dir = UPLOAD_DIR / proj["id"]
    phase_blocks = ""
    for ph in PHASES:
        ph_dir = proj_dir / ph["key"]
        files_html = ""
        if ph_dir.exists():
            files = list(ph_dir.iterdir())
            files_html = "".join(f"<li>{file_icon(f.name)} {f.name}</li>" for f in files) if files else "<li><i>No files uploaded</i></li>"
        else:
            files_html = "<li><i>No files uploaded</i></li>"
        phase_blocks += f"""
        <div class="phase-block" style="border-left:5px solid {ph['color']}">
            <h3 style="color:{ph['color']};margin:0 0 0.6rem">{ph['icon']} {ph['label']}</h3>
            <ul>{files_html}</ul>
        </div>"""

    tags_html = "".join(
        f'<span class="tag" style="background:{TYPE_COLORS[i%len(TYPE_COLORS)]}">{s}</span>'
        for i,s in enumerate(proj.get("styles",[]))
    )
    sc = STATUS_COLORS.get(proj.get("status",""), "#6366f1")

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>{proj['name']} — Project Report</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Nunito:wght@400;600&display=swap');
body {{ font-family:'Nunito',sans-serif; background:#f8f6ff; color:#1a1a2e; margin:0; padding:0; }}
.hero {{ background:linear-gradient(135deg,#667eea,#764ba2,#f64f59); color:white; padding:2.5rem 3rem; }}
.hero h1 {{ font-family:'Playfair Display',serif; font-size:2.4rem; margin:0; }}
.hero .sub {{ opacity:.85; margin-top:.5rem; font-size:1.05rem; }}
.body {{ max-width:900px; margin:0 auto; padding:2rem; }}
.meta-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin:1.5rem 0; }}
.meta-item {{ background:white; border-radius:12px; padding:1rem 1.4rem; box-shadow:0 2px 10px rgba(0,0,0,.07); }}
.meta-item .key {{ font-size:.75rem; text-transform:uppercase; letter-spacing:.1em; color:#9ca3af; font-weight:600; }}
.meta-item .val {{ font-size:1.1rem; font-weight:700; color:#1a1a2e; margin-top:2px; }}
.section-title {{ font-family:'Playfair Display',serif; font-size:1.5rem; margin:2rem 0 1rem; color:#5b21b6; border-bottom:2px solid #ede9fe; padding-bottom:.4rem; }}
.desc-box {{ background:white; border-radius:12px; padding:1.4rem; box-shadow:0 2px 10px rgba(0,0,0,.07); line-height:1.7; }}
.phase-block {{ background:white; border-radius:12px; padding:1.2rem 1.5rem; margin-bottom:1rem; box-shadow:0 2px 10px rgba(0,0,0,.07); }}
.phase-block ul {{ margin:.5rem 0 0; padding-left:1.2rem; color:#374151; }}
.phase-block li {{ padding:3px 0; }}
.tag {{ display:inline-block; border-radius:20px; padding:3px 12px; font-size:.8rem; margin:3px; font-weight:700; color:white; }}
.status {{ background:{sc}; color:white; border-radius:20px; padding:4px 14px; font-size:.85rem; font-weight:700; }}
.footer {{ text-align:center; color:#9ca3af; font-size:.8rem; margin-top:3rem; padding:1rem; border-top:1px solid #ede9fe; }}
@media print {{ body {{ background:white; }} .hero {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }} }}
</style>
</head>
<body>
<div class="hero">
  <h1>{proj['name']}</h1>
  <div class="sub">{proj.get('project_type','')} &nbsp;|&nbsp; {proj.get('area','')} &nbsp;|&nbsp; {proj.get('year','')} &nbsp;&nbsp; <span class="status">{proj.get('status','')}</span></div>
</div>
<div class="body">
  <div class="meta-grid">
    <div class="meta-item"><div class="key">Client</div><div class="val">{proj.get('client','—')}</div></div>
    <div class="meta-item"><div class="key">Budget Range</div><div class="val">{proj.get('budget_range','—')}</div></div>
    <div class="meta-item"><div class="key">Year</div><div class="val">{proj.get('year','—')}</div></div>
    <div class="meta-item"><div class="key">Project Type</div><div class="val">{proj.get('project_type','—')}</div></div>
  </div>
  {"<div class='section-title'>Design Styles</div><div>" + tags_html + "</div>" if tags_html else ""}
  {"<div class='section-title'>Project Description</div><div class='desc-box'>" + proj.get('description','') + "</div>" if proj.get('description') else ""}
  {"<div class='section-title'>Notes</div><div class='desc-box'>" + proj.get('notes','') + "</div>" if proj.get('notes') else ""}
  <div class="section-title">Design Phases &amp; Files</div>
  {phase_blocks}
  <div class="footer">Studio Archive &nbsp;·&nbsp; Generated {datetime.now().strftime('%d %B %Y at %H:%M')}</div>
</div>
</body></html>"""
    return html.encode("utf-8")


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏛️ Studio Archive</div>', unsafe_allow_html=True)
    st.markdown("*Interior Design Portfolio Database*")
    st.markdown("---")
    page = st.radio("", ["📂  All Projects", "➕  Add New Project", "📊  Statistics"], label_visibility="collapsed")
    st.markdown("---")
    projects = load_projects()
    completed_count = sum(1 for p in projects if p.get("status") == "Completed")
    inprog_count    = sum(1 for p in projects if p.get("status") == "In Progress")
    st.markdown(f"**{len(projects)}** total &nbsp;·&nbsp; **{completed_count}** done &nbsp;·&nbsp; **{inprog_count}** active")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL PROJECTS
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📂  All Projects":
    st.markdown("""
    <div class="hero-header">
        <h1>📂 All Projects</h1>
        <p>Your complete interior design portfolio — search, filter, view & export</p>
    </div>""", unsafe_allow_html=True)

    if not projects:
        st.info("No projects yet. Go to **Add New Project** to get started!")
    else:
        col1, col2, col3, col4 = st.columns([3,2,2,2])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Name, client, description...")
        with col2:
            all_types  = ["All"] + sorted(set(p["project_type"] for p in projects))
            type_filter = st.selectbox("Type", all_types)
        with col3:
            all_years  = ["All"] + sorted(set(str(p["year"]) for p in projects), reverse=True)
            year_filter = st.selectbox("Year", all_years)
        with col4:
            all_stat   = ["All"] + sorted(set(p.get("status","") for p in projects))
            stat_filter = st.selectbox("Status", all_stat)

        filtered = projects[:]
        if search:
            q = search.lower()
            filtered = [p for p in filtered if q in p.get("name","").lower()
                        or q in p.get("client","").lower()
                        or q in p.get("description","").lower()]
        if type_filter != "All":
            filtered = [p for p in filtered if p["project_type"] == type_filter]
        if year_filter != "All":
            filtered = [p for p in filtered if str(p["year"]) == year_filter]
        if stat_filter != "All":
            filtered = [p for p in filtered if p.get("status") == stat_filter]

        st.caption(f"Showing **{len(filtered)}** of **{len(projects)}** projects")
        st.markdown("---")

        for proj in reversed(filtered):
            proj_dir     = UPLOAD_DIR / proj["id"]
            status_color = STATUS_COLORS.get(proj.get("status",""), "#6366f1")
            all_types_list = list(dict.fromkeys(p["project_type"] for p in projects))
            tidx  = all_types_list.index(proj["project_type"]) if proj["project_type"] in all_types_list else 0
            accent = TYPE_COLORS[tidx % len(TYPE_COLORS)]
            thumb  = get_thumbnail(proj_dir)

            # Project "webpage" card header
            st.markdown(f"""
            <div class="proj-page" style="border-top-color:{accent};">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
                <div>
                  <h2 style="margin:0;color:#1a1a2e;">{proj['name']}</h2>
                  <div style="color:#6b7280;margin-top:5px;font-size:0.95rem;">
                    🏢 {proj.get('project_type','—')} &nbsp;|&nbsp;
                    📍 {proj.get('area','—')} &nbsp;|&nbsp;
                    📅 {proj.get('year','—')} &nbsp;|&nbsp;
                    👤 {proj.get('client','—')}
                    {"&nbsp;|&nbsp; 💰 " + proj.get('budget_range','') if proj.get('budget_range') and proj.get('budget_range') != '—' else ''}
                  </div>
                </div>
                <span style="background:{status_color};color:white;border-radius:20px;padding:5px 16px;font-size:0.85rem;font-weight:700;white-space:nowrap;">{proj.get('status','—')}</span>
              </div>
            </div>""", unsafe_allow_html=True)

            # Thumbnail + description
            if thumb:
                ci, cd = st.columns([1, 2])
                with ci:
                    st.image(str(thumb), use_container_width=True)
                with cd:
                    if proj.get("description"):
                        st.markdown(proj["description"])
                    if proj.get("styles"):
                        tags = "".join(f'<span class="tag" style="background:{TYPE_COLORS[i%len(TYPE_COLORS)]}">{s}</span>'
                                       for i,s in enumerate(proj["styles"]))
                        st.markdown(tags, unsafe_allow_html=True)
            else:
                if proj.get("description"):
                    st.markdown(proj["description"])
                if proj.get("styles"):
                    tags = "".join(f'<span class="tag" style="background:{TYPE_COLORS[i%len(TYPE_COLORS)]}">{s}</span>'
                                   for i,s in enumerate(proj["styles"]))
                    st.markdown(tags, unsafe_allow_html=True)

            # Design phases
            st.markdown("#### 📁 Design Phases")
            ph_cols = st.columns(4)
            for i, ph in enumerate(PHASES):
                ph_dir = proj_dir / ph["key"]
                files  = list(ph_dir.iterdir()) if ph_dir.exists() else []
                with ph_cols[i]:
                    file_lines = "<br>".join(
                        f'{file_icon(f.name)} {f.name[:22]}{"…" if len(f.name)>22 else ""}'
                        for f in files
                    ) if files else "<i style='color:#9ca3af'>No files yet</i>"
                    st.markdown(f"""
                    <div class="phase-card" style="border-left-color:{ph['color']};">
                      <div style="font-weight:700;color:{ph['color']};font-size:0.82rem;">{ph['icon']} Phase {i+1}</div>
                      <div style="font-size:0.75rem;color:#4b5563;margin:3px 0 8px;">{ph['label'].split('—',1)[1].strip()}</div>
                      <div style="font-size:0.8rem;color:#374151;line-height:1.6;">{file_lines}</div>
                    </div>""", unsafe_allow_html=True)

                    # Per-phase download buttons
                    if files:
                        with st.expander("⬇️ Download", expanded=False):
                            for f in files:
                                with open(f, "rb") as fh:
                                    st.download_button(
                                        label=f"{file_icon(f.name)} {f.name}",
                                        data=fh.read(),
                                        file_name=f.name,
                                        key=f"dl_{proj['id']}_{ph['key']}_{f.name}"
                                    )

            # Export row
            st.markdown("**Export full project:**")
            e1, e2, e3, _, d1 = st.columns([2, 2, 2, 2, 1])

            with e1:
                excel_data = export_excel(proj)
                if excel_data:
                    st.download_button("📊 Excel", data=excel_data,
                                       file_name=f"{proj['name'][:30].replace(' ','_')}_report.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                       key=f"xl_{proj['id']}", use_container_width=True)
                else:
                    st.caption("pip install openpyxl")

            with e2:
                docx_data = export_docx(proj)
                if docx_data:
                    st.download_button("📝 Word (.docx)", data=docx_data,
                                       file_name=f"{proj['name'][:30].replace(' ','_')}_report.docx",
                                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                       key=f"docx_{proj['id']}", use_container_width=True)
                else:
                    st.caption("pip install python-docx")

            with e3:
                html_data = export_html_report(proj)
                st.download_button("🖨️ PDF Report (HTML)", data=html_data,
                                   file_name=f"{proj['name'][:30].replace(' ','_')}_report.html",
                                   mime="text/html",
                                   key=f"html_{proj['id']}", use_container_width=True)

            with d1:
                if st.button("🗑️", key=f"del_{proj['id']}", help="Delete this project"):
                    st.session_state[f"confirm_{proj['id']}"] = True

            if st.session_state.get(f"confirm_{proj['id']}"):
                st.warning(f"⚠️ Delete **{proj['name']}**? This cannot be undone.")
                ya, na = st.columns(2)
                if ya.button("✅ Yes, delete", key=f"yes_{proj['id']}"):
                    projects = [p for p in projects if p["id"] != proj["id"]]
                    save_projects(projects)
                    if proj_dir.exists():
                        shutil.rmtree(proj_dir)
                    st.rerun()
                if na.button("❌ Cancel", key=f"no_{proj['id']}"):
                    st.session_state[f"confirm_{proj['id']}"] = False
                    st.rerun()

            st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD NEW PROJECT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕  Add New Project":
    st.markdown("""
    <div class="hero-header" style="background:linear-gradient(135deg,#f093fb,#f5576c,#fda085);">
        <h1>➕ Add New Project</h1>
        <p>Fill in details and upload files per design phase, then save</p>
    </div>""", unsafe_allow_html=True)

    with st.form("add_form", clear_on_submit=True):
        st.markdown("### 📋 Project Details")
        c1, c2 = st.columns(2)
        with c1:
            name         = st.text_input("Project Name *", placeholder="e.g. Verma Residence — Master Bedroom")
            client       = st.text_input("Client Name",    placeholder="e.g. Mr. & Mrs. Verma")
            year         = st.number_input("Year *", min_value=2000, max_value=2100, value=datetime.now().year)
            area         = st.text_input("Area / Location", placeholder="e.g. Jubilee Hills, Hyderabad")
        with c2:
            project_type = st.selectbox("Project Type *", [
                "Residential","Commercial","Office","Hospitality",
                "Retail","Healthcare","Educational","Renovation","Other"
            ])
            budget_range = st.selectbox("Budget Range", ["—","Under ₹5L","₹5L–₹20L","₹20L–₹50L","₹50L–₹1Cr","₹1Cr+"])
            status       = st.selectbox("Project Status", ["Completed","In Progress","Concept / Proposal","On Hold"])

        description = st.text_area("Project Description", placeholder="Your vision, design approach, challenges, outcomes...", height=120)

        style_options = ["Contemporary","Modern","Minimalist","Traditional","Bohemian",
                         "Industrial","Scandinavian","Art Deco","Rustic","Eclectic",
                         "Luxury","Mid-Century Modern","Vastu-Compliant","Sustainable","Smart Home"]
        styles      = st.multiselect("Design Styles", style_options)
        custom_tags = st.text_input("Custom style tags (comma-separated)", placeholder="e.g. Open Plan, Passive Cooling")

        st.markdown("---")
        st.markdown("### 📁 Upload Files — by Design Phase")
        st.caption("Accepts CAD (.dwg .dxf .rvt .skp), Images (.jpg .png), 3D models (.obj .fbx .blend), PDFs, Videos, and any other file format.")

        phase_files = {}
        for ph in PHASES:
            st.markdown(f"""
            <div style="background:white;border-left:5px solid {ph['color']};border-radius:10px;
                        padding:0.8rem 1.2rem;margin:0.6rem 0 0.2rem;">
                <span style="color:{ph['color']};font-weight:700;font-size:1rem;">{ph['icon']} {ph['label']}</span>
            </div>""", unsafe_allow_html=True)
            phase_files[ph["key"]] = st.file_uploader(
                f"drop_{ph['key']}",
                accept_multiple_files=True,
                key=f"up_{ph['key']}",
                label_visibility="collapsed"
            )

        st.markdown("---")
        notes    = st.text_area("Additional Notes", placeholder="Software used, key vendors, materials, awards, site measurements...")
        submitted = st.form_submit_button("💾 Save Project", use_container_width=True)

    if submitted:
        if not name:
            st.error("Project name is required!")
        else:
            proj_id    = f"{int(datetime.now().timestamp())}_{name[:20].replace(' ','_').lower()}"
            all_styles = styles + [s.strip() for s in custom_tags.split(",") if s.strip()]
            total_files = sum(len(v) for v in phase_files.values() if v)

            new_proj = {
                "id": proj_id, "name": name, "client": client,
                "year": int(year), "project_type": project_type, "area": area,
                "budget_range": budget_range, "description": description,
                "styles": all_styles, "status": status, "notes": notes,
                "created_at": datetime.now().isoformat(), "file_count": total_files
            }

            proj_dir = UPLOAD_DIR / proj_id
            for ph in PHASES:
                files = phase_files.get(ph["key"]) or []
                if files:
                    ph_dir = proj_dir / ph["key"]
                    ph_dir.mkdir(parents=True, exist_ok=True)
                    for uf in files:
                        with open(ph_dir / uf.name, "wb") as fh:
                            fh.write(uf.getbuffer())

            projects.append(new_proj)
            save_projects(projects)
            st.success(f"✅ **{name}** saved with **{total_files}** files across all phases!")
            st.balloons()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊  Statistics":
    st.markdown("""
    <div class="hero-header" style="background:linear-gradient(135deg,#4facfe,#00f2fe,#43e97b);">
        <h1>📊 Studio Statistics</h1>
        <p>Overview of your entire interior design practice</p>
    </div>""", unsafe_allow_html=True)

    if not projects:
        st.info("No projects yet.")
    else:
        total_files = sum(
            sum(len(list((UPLOAD_DIR / p["id"] / ph["key"]).iterdir()))
                for ph in PHASES if (UPLOAD_DIR / p["id"] / ph["key"]).exists())
            for p in projects
        )
        completed    = sum(1 for p in projects if p.get("status") == "Completed")
        in_prog      = sum(1 for p in projects if p.get("status") == "In Progress")
        years_active = len(set(p["year"] for p in projects))

        cols = st.columns(5)
        for col, num, label, color in zip(cols, [
            len(projects), completed, in_prog, total_files, years_active
        ], ["Total Projects","Completed","In Progress","Total Files","Years Active"],
           ["#667eea","#10b981","#f59e0b","#f64f59","#a29bfe"]):
            with col:
                st.markdown(f"""
                <div class="stat-box" style="background:linear-gradient(135deg,{color},{color}bb);">
                    <div class="stat-num">{num}</div>
                    <div class="stat-label">{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        ca, cb = st.columns(2)
        with ca:
            st.markdown("#### Projects by Type")
            st.bar_chart(dict(collections.Counter(p["project_type"] for p in projects)))
        with cb:
            st.markdown("#### Projects by Year")
            st.bar_chart(dict(sorted(collections.Counter(p["year"] for p in projects).items())))

        cc, cd = st.columns(2)
        with cc:
            st.markdown("#### Status Breakdown")
            st.bar_chart(dict(collections.Counter(p.get("status","—") for p in projects)))
        with cd:
            st.markdown("#### Top Design Styles")
            flat = [s for p in projects for s in p.get("styles",[])]
            if flat:
                top = collections.Counter(flat).most_common(8)
                for sty, cnt in top:
                    st.progress(cnt / top[0][1], text=f"{sty} ({cnt})")

        st.markdown("---")
        st.markdown("#### Recent Projects")
        for p in sorted(projects, key=lambda x: x.get("created_at",""), reverse=True)[:8]:
            sc = STATUS_COLORS.get(p.get("status",""), "#999")
            st.markdown(
                f"**{p['name']}** — {p['project_type']}, {p['year']} &nbsp;"
                f"<span style='background:{sc};color:white;padding:2px 10px;border-radius:10px;font-size:.8rem'>{p.get('status','—')}</span>",
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown("#### Backup All Data")
        st.download_button("⬇️ Download metadata backup (JSON)",
                           data=json.dumps(projects, indent=2),
                           file_name="studio_archive_backup.json",
                           mime="application/json")
