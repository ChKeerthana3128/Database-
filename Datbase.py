import streamlit as st
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import base64

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Design Studio — Portfolio DB",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = Path("data")
PROJECTS_FILE = DATA_DIR / "projects.json"
UPLOADS_DIR = DATA_DIR / "uploads"

# Create dirs if they don't exist
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 { font-family: 'Cormorant Garamond', serif; font-weight: 300; letter-spacing: 0.05em; }

.main { background: #faf9f7; }

.project-card {
    background: white;
    border: 1px solid #e8e4de;
    border-radius: 4px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
}
.project-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.08); }

.tag {
    display: inline-block;
    background: #f0ede8;
    color: #5c5449;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    margin: 2px;
    font-family: 'DM Sans', sans-serif;
}

.stat-box {
    background: #1a1814;
    color: #f0ede8;
    padding: 1.5rem;
    border-radius: 4px;
    text-align: center;
}
.stat-num { font-family: 'Cormorant Garamond', serif; font-size: 2.5rem; font-weight: 300; }
.stat-label { font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0.6; }

.section-divider {
    border: none;
    border-top: 1px solid #e8e4de;
    margin: 2rem 0;
}

.file-chip {
    background: #f5f2ee;
    border: 1px solid #ddd9d3;
    border-radius: 3px;
    padding: 4px 10px;
    font-size: 0.78rem;
    color: #5c5449;
    margin: 2px;
    display: inline-block;
}

.sidebar-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.4rem;
    font-weight: 300;
    letter-spacing: 0.1em;
    color: #1a1814;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_projects():
    if PROJECTS_FILE.exists():
        with open(PROJECTS_FILE) as f:
            return json.load(f)
    return []

def save_projects(projects):
    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects, f, indent=2)

def get_file_icon(filename):
    ext = Path(filename).suffix.lower()
    icons = {
        ".dwg": "📐", ".dxf": "📐", ".rvt": "📐", ".skp": "📐",
        ".jpg": "🖼️", ".jpeg": "🖼️", ".png": "🖼️", ".gif": "🖼️",
        ".pdf": "📄", ".mp4": "🎬", ".mov": "🎬", ".avi": "🎬",
        ".obj": "🧊", ".fbx": "🧊", ".3ds": "🧊", ".blend": "🧊",
        ".xlsx": "📊", ".csv": "📊", ".pptx": "📊",
        ".zip": "🗜️", ".rar": "🗜️",
    }
    return icons.get(ext, "📎")

def get_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🏛️ STUDIO ARCHIVE</div>', unsafe_allow_html=True)
    st.markdown("*Your interior design portfolio database*")
    st.markdown("---")
    page = st.radio("Navigate", ["📂 All Projects", "➕ Add New Project", "📊 Statistics"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Files are saved locally in `data/uploads/`")
    st.caption("Export your data anytime from the Statistics page")

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
projects = load_projects()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL PROJECTS
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📂 All Projects":
    st.markdown("## All Projects")

    if not projects:
        st.info("No projects yet. Go to **Add New Project** to get started!")
    else:
        # ── Filters ──
        col1, col2, col3, col4 = st.columns([3,2,2,2])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Project name, client, keyword...")
        with col2:
            all_types = sorted(set(p["project_type"] for p in projects))
            type_filter = st.selectbox("Type", ["All"] + all_types)
        with col3:
            all_years = sorted(set(p["year"] for p in projects), reverse=True)
            year_filter = st.selectbox("Year", ["All"] + [str(y) for y in all_years])
        with col4:
            all_styles = sorted(set(s for p in projects for s in p.get("styles", [])))
            style_filter = st.selectbox("Style", ["All"] + all_styles)

        # ── Apply Filters ──
        filtered = projects
        if search:
            q = search.lower()
            filtered = [p for p in filtered if q in p["name"].lower() or q in p.get("client","").lower() or q in p.get("description","").lower()]
        if type_filter != "All":
            filtered = [p for p in filtered if p["project_type"] == type_filter]
        if year_filter != "All":
            filtered = [p for p in filtered if str(p["year"]) == year_filter]
        if style_filter != "All":
            filtered = [p for p in filtered if style_filter in p.get("styles", [])]

        st.caption(f"Showing {len(filtered)} of {len(projects)} projects")
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # ── Project Cards ──
        for i, proj in enumerate(reversed(filtered)):
            proj_dir = UPLOADS_DIR / proj["id"]

            with st.container():
                # Find a thumbnail image if any
                preview_img = None
                if proj_dir.exists():
                    for f in proj_dir.iterdir():
                        if f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                            preview_img = f
                            break

                c1, c2 = st.columns([1, 3] if preview_img else [0.001, 1])
                if preview_img:
                    with c1:
                        st.image(str(preview_img), use_container_width=True)

                with c2:
                    st.markdown(f"### {proj['name']}")
                    meta_cols = st.columns(4)
                    meta_cols[0].markdown(f"**Type:** {proj['project_type']}")
                    meta_cols[1].markdown(f"**Year:** {proj['year']}")
                    meta_cols[2].markdown(f"**Client:** {proj.get('client','—')}")
                    meta_cols[3].markdown(f"**Area:** {proj.get('area','—')}")

                    if proj.get("description"):
                        st.markdown(proj["description"])

                    # Styles
                    if proj.get("styles"):
                        tags_html = "".join(f'<span class="tag">{s}</span>' for s in proj["styles"])
                        st.markdown(tags_html, unsafe_allow_html=True)

                    # Files
                    if proj_dir.exists():
                        files = list(proj_dir.iterdir())
                        if files:
                            st.markdown("**Files:**")
                            chips = ""
                            for f in files:
                                icon = get_file_icon(f.name)
                                chips += f'<span class="file-chip">{icon} {f.name}</span> '
                            st.markdown(chips, unsafe_allow_html=True)

                            # Download buttons
                            with st.expander("⬇️ Download files"):
                                for f in files:
                                    with open(f, "rb") as fh:
                                        st.download_button(
                                            label=f"{get_file_icon(f.name)} {f.name}",
                                            data=fh.read(),
                                            file_name=f.name,
                                            key=f"dl_{proj['id']}_{f.name}"
                                        )

                    # Delete button (with confirm)
                    if st.button(f"🗑️ Delete project", key=f"del_{proj['id']}"):
                        st.session_state[f"confirm_del_{proj['id']}"] = True

                    if st.session_state.get(f"confirm_del_{proj['id']}"):
                        st.warning(f"Are you sure you want to delete **{proj['name']}**?")
                        c_yes, c_no = st.columns(2)
                        if c_yes.button("Yes, delete", key=f"yes_{proj['id']}"):
                            projects = [p for p in projects if p["id"] != proj["id"]]
                            save_projects(projects)
                            if proj_dir.exists():
                                shutil.rmtree(proj_dir)
                            st.rerun()
                        if c_no.button("Cancel", key=f"no_{proj['id']}"):
                            st.session_state[f"confirm_del_{proj['id']}"] = False
                            st.rerun()

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD NEW PROJECT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add New Project":
    st.markdown("## Add New Project")
    st.markdown("Fill in the details and upload all files related to this project.")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    with st.form("new_project_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Project Name *", placeholder="e.g. Sharma Residence — Living Room Redesign")
            client = st.text_input("Client Name", placeholder="e.g. Mr. & Mrs. Sharma")
            year = st.number_input("Year *", min_value=2000, max_value=2100, value=datetime.now().year)
        with c2:
            project_type = st.selectbox("Project Type *", [
                "Residential", "Commercial", "Office", "Hospitality",
                "Retail", "Healthcare", "Educational", "Renovation", "Other"
            ])
            area = st.text_input("Area / Location", placeholder="e.g. Banjara Hills, Hyderabad")
            budget_range = st.selectbox("Budget Range", ["—", "Under ₹5L", "₹5L–₹20L", "₹20L–₹50L", "₹50L+"])

        description = st.text_area("Project Description", placeholder="Brief about the project, your approach, challenges, outcomes...")

        style_options = ["Contemporary", "Modern", "Minimalist", "Traditional", "Bohemian",
                         "Industrial", "Scandinavian", "Art Deco", "Rustic", "Eclectic", "Luxury", "Mid-Century Modern"]
        styles = st.multiselect("Design Styles", style_options)

        custom_styles = st.text_input("Custom style tags (comma-separated)", placeholder="e.g. Vastu-compliant, Sustainable, Smart Home")

        status = st.selectbox("Project Status", ["Completed", "In Progress", "Concept / Proposal", "On Hold"])

        st.markdown("#### 📁 Upload Files")
        st.caption("Supports CAD (.dwg, .dxf, .rvt, .skp), Images (.jpg, .png), 3D (.obj, .fbx, .blend), PDF, Video, and more")
        uploaded_files = st.file_uploader(
            "Upload all project files",
            accept_multiple_files=True,
            type=None  # Accept all file types
        )

        notes = st.text_area("Additional Notes", placeholder="Software used, materials, vendors, special mentions...")

        submitted = st.form_submit_button("💾 Save Project", use_container_width=True)

    if submitted:
        if not name:
            st.error("Project name is required!")
        else:
            # Build project record
            proj_id = f"{int(datetime.now().timestamp())}_{name[:20].replace(' ','_').lower()}"
            all_styles = styles + [s.strip() for s in custom_styles.split(",") if s.strip()]

            new_project = {
                "id": proj_id,
                "name": name,
                "client": client,
                "year": int(year),
                "project_type": project_type,
                "area": area,
                "budget_range": budget_range,
                "description": description,
                "styles": all_styles,
                "status": status,
                "notes": notes,
                "created_at": datetime.now().isoformat(),
                "file_count": len(uploaded_files) if uploaded_files else 0
            }

            # Save files
            proj_dir = UPLOADS_DIR / proj_id
            proj_dir.mkdir(parents=True, exist_ok=True)
            if uploaded_files:
                for uf in uploaded_files:
                    with open(proj_dir / uf.name, "wb") as f:
                        f.write(uf.getbuffer())

            # Save project
            projects.append(new_project)
            save_projects(projects)

            st.success(f"✅ **{name}** saved successfully with {len(uploaded_files) if uploaded_files else 0} files!")
            st.balloons()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Statistics":
    st.markdown("## Studio Statistics")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    if not projects:
        st.info("No projects yet to show statistics.")
    else:
        # ── Top Stats ──
        total_files = sum(
            len(list((UPLOADS_DIR / p["id"]).iterdir()))
            if (UPLOADS_DIR / p["id"]).exists() else p.get("file_count", 0)
            for p in projects
        )
        completed = sum(1 for p in projects if p.get("status") == "Completed")
        years_active = len(set(p["year"] for p in projects))

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{len(projects)}</div><div class="stat-label">Total Projects</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{completed}</div><div class="stat-label">Completed</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{total_files}</div><div class="stat-label">Total Files</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{years_active}</div><div class="stat-label">Years Active</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts ──
        import collections
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### Projects by Type")
            type_counts = collections.Counter(p["project_type"] for p in projects)
            st.bar_chart(dict(type_counts))

        with c2:
            st.markdown("#### Projects by Year")
            year_counts = collections.Counter(p["year"] for p in projects)
            st.bar_chart(dict(sorted(year_counts.items())))

        # ── Style breakdown ──
        all_styles_flat = [s for p in projects for s in p.get("styles", [])]
        if all_styles_flat:
            st.markdown("#### Top Design Styles")
            style_counts = collections.Counter(all_styles_flat).most_common(10)
            for style, count in style_counts:
                st.progress(count / max(c for _, c in style_counts), text=f"{style} ({count})")

        # ── Recent Projects ──
        st.markdown("#### Recent Projects")
        recent = sorted(projects, key=lambda p: p.get("created_at",""), reverse=True)[:5]
        for p in recent:
            st.markdown(f"- **{p['name']}** — {p['project_type']}, {p['year']} ({p.get('status','—')})")

        # ── Export ──
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("#### Export Data")
        st.download_button(
            "⬇️ Download all project metadata (JSON)",
            data=json.dumps(projects, indent=2),
            file_name="studio_archive.json",
            mime="application/json"
        )
