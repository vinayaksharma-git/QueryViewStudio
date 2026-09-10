import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import json
import io
import zipfile

# 1. Page Configuration
st.set_page_config(
    page_title="Query View Studio",
    page_icon="🔎",
    layout="wide"
)

# Custom CSS for spacing and smooth transitions (allows manual drag resizing & auto-expansion)
st.markdown("""
    <style>
        /* Allow sidebar flexibility while ensuring vertical spacing */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        
        /* Space out inputs inside sidebar for easier selection */
        [data-testid="stSidebar"] .stSelectbox, 
        [data-testid="stSidebar"] .stFileUploader, 
        [data-testid="stSidebar"] .stButton {
            margin-bottom: 12px;
        }

        /* Ensure main canvas expands dynamically to fill remaining area */
        [data-testid="stMainBlockContainer"] {
            max-width: 100% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "cells" not in st.session_state:
    st.session_state.cells = []
if "df" not in st.session_state:
    st.session_state.df = None

# Header row with title only
st.title("⌕ Query View Studio")

# Sidebar: Project Bundle & Dataset Management
with st.sidebar:
    st.header("🗀 Project Bundle")
    
    # Save project and dataset bundle together into a zip file
    if st.session_state.cells and st.session_state.df is not None:
        project_data = []
        for cell in st.session_state.cells:
            project_data.append({
                "type": cell["type"],
                "content": cell.get("content", ""),
                "viz_type": cell["viz_type"],
                "x_col": cell.get("x_col"),
                "y_col": cell.get("y_col"),
                "filters": cell.get("filters", [])
            })
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("project.json", json.dumps(project_data, indent=4))
            zip_file.writestr("dataset.csv", st.session_state.df.to_csv(index=False))
        
        st.download_button(
            label="⎙ Save Project Bundle",
            data=zip_buffer.getvalue(),
            file_name="datacanvas_project.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    # Load saved project zip bundle and automatically extract dataset and queries
    uploaded_bundle = st.file_uploader("Load Project Bundle", type=["zip"])
    if uploaded_bundle is not None:
        try:
            with zipfile.ZipFile(uploaded_bundle, "r") as zip_file:
                if "project.json" in zip_file.namelist() and "dataset.csv" in zip_file.namelist():
                    dataset_bytes = zip_file.read("dataset.csv")
                    st.session_state.df = pd.read_csv(io.BytesIO(dataset_bytes))
                    
                    project_bytes = zip_file.read("project.json")
                    loaded_data = json.loads(project_bytes.decode("utf-8"))
                    
                    st.session_state.cells = []
                    for idx, item in enumerate(loaded_data):
                        cell_type = item["type"]
                        content_val = item.get("content", "")
                        
                        # Preload output_data for Markdown cells automatically upon load
                        out_data = content_val if "Markdown" in cell_type else None
                        
                        st.session_state.cells.append({
                            "id": str(idx),
                            "type": cell_type,
                            "content": content_val,
                            "viz_type": item["viz_type"],
                            "x_col": item.get("x_col"),
                            "y_col": item.get("y_col"),
                            "filters": item.get("filters", []),
                            "output_data": out_data
                        })
                    st.success("Project bundle loaded successfully, remove bundle to get started - click ⓧ")
                    st.rerun()
                else:
                    st.error("Invalid bundle structure. Missing project.json or dataset.csv.")
        except Exception as e:
            st.error(f"Error loading bundle: {e}")

    # Spacing between sections
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
    st.header("𝄜 Load Dataset")
    uploaded_file = st.file_uploader("Upload CSV, Excel, or JSON", type=["csv", "xlsx", "json"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                st.session_state.df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                st.session_state.df = pd.read_json(uploaded_file)
            st.success("Dataset loaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {e}")

    # Spacing between sections
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
    st.header("☰ Add Cell")
    cell_type = st.selectbox("Cell Type", ["SQL Query", "Pandas Query", "Power BI / Excel View", "Markdown"])
    
    if st.button("✚ Insert Cell", use_container_width=True):
        new_id = str(len(st.session_state.cells))
        new_cell = {
            "id": new_id,
            "type": cell_type,
            "content": "",
            "viz_type": "Bar Chart" if "Query" in cell_type or "View" in cell_type else "None",
            "x_col": None,
            "y_col": None,
            "filters": [],
            "output_data": None
        }
        st.session_state.cells.append(new_cell)
        st.rerun()

# Main Interface: Split Screen (Left: Editor, Right: Canvas) — Only rendered if dataset is present
if st.session_state.df is not None:
    df = st.session_state.df
    columns_list = df.columns.tolist()
    dropdown_options = ["-- None / Select Field --"] + columns_list
    
    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        st.subheader("🗐 Notebook Editor")
        
        if not st.session_state.cells:
            st.info("Use the sidebar to add your first cell.")
            
        for i, cell in enumerate(st.session_state.cells):
            with st.container(border=True):
                st.markdown(f"**Cell {i} : {cell['type']}**")
                
                if "Markdown" in cell['type']:
                    cell['content'] = st.text_area(
                        "Markdown Code (# Heading, ## Subheading, Text)",
                        value=cell['content'],
                        key=f"content_{i}"
                    )
                    cell['output_data'] = cell['content']
                
                elif "SQL Query" in cell['type']:
                    cell['content'] = st.text_area(
                        "SQL Query (Table name: `df`)",
                        value=cell['content'],
                        key=f"content_{i}"
                    )
                    
                    viz_options = ["Table", "Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Area Chart"]
                    default_idx = viz_options.index(cell['viz_type']) if cell['viz_type'] in viz_options else 1
                    
                    cell['viz_type'] = st.selectbox(
                        "Power BI Style Visual",
                        viz_options,
                        index=default_idx,
                        key=f"viz_{i}"
                    )
                    
                    if st.button("▶ Run SQL", key=f"run_{i}"):
                        try:
                            res_df = duckdb.query(cell['content']).df()
                            cell['output_data'] = res_df
                            st.success("Executed!")
                        except Exception as e:
                            st.error(f"SQL Error: {e}")

                elif "Pandas Query" in cell['type']:
                    cell['content'] = st.text_area(
                        "Pandas Code (Result as `result_df`, DataFrame is `df`)",
                        value=cell['content'],
                        key=f"content_{i}",
                        placeholder="result_df = df.head(5)"
                    )
                    
                    viz_options = ["Table", "Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Area Chart"]
                    default_idx = viz_options.index(cell['viz_type']) if cell['viz_type'] in viz_options else 1
                    
                    cell['viz_type'] = st.selectbox(
                        "Power BI Style Visual",
                        viz_options,
                        index=default_idx,
                        key=f"viz_{i}"
                    )
                    
                    if st.button("▶ Run Pandas", key=f"run_{i}"):
                        try:
                            local_vars = {"df": df, "pd": pd}
                            exec(cell['content'], {}, local_vars)
                            cell['output_data'] = local_vars.get("result_df", None)
                            st.success("Executed!")
                        except Exception as e:
                            st.error(f"Pandas Error: {e}")

                elif "Power BI / Excel View" in cell['type']:
                    viz_options = ["Table", "Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Area Chart"]
                    default_idx = viz_options.index(cell['viz_type']) if cell['viz_type'] in viz_options else 1
                    cell['viz_type'] = st.selectbox(
                        "Power BI / Excel Style Visual",
                        viz_options,
                        index=default_idx,
                        key=f"viz_{i}"
                    )

                    # Interactive Axis selectors from dropdown
                    if cell['viz_type'] != "Table":
                        x_curr_idx = dropdown_options.index(cell['x_col']) if cell['x_col'] in dropdown_options else 0
                        y_curr_idx = dropdown_options.index(cell['y_col']) if cell['y_col'] in dropdown_options else 0
                        
                        selected_x = st.selectbox("X-Axis Field", dropdown_options, index=x_curr_idx, key=f"x_col_{i}")
                        selected_y = st.selectbox("Y-Axis Field", dropdown_options, index=y_curr_idx, key=f"y_col_{i}")
                        
                        cell['x_col'] = selected_x if selected_x != "-- None / Select Field --" else None
                        cell['y_col'] = selected_y if selected_y != "-- None / Select Field --" else None

                    # Filter Options builder (Multi-Value Selection)
                    st.markdown("##### 🔍 Filter Options")
                    if "filters" not in cell:
                        cell["filters"] = []
                    
                    f_col_selection = st.selectbox("Filter Column", dropdown_options, index=0, key=f"f_col_{i}")
                    
                    f_val_selections = []
                    if f_col_selection != "-- None / Select Field --":
                        unique_vals = [str(v) for v in df[f_col_selection].dropna().unique().tolist()]
                        f_val_selections = st.multiselect("Filter Value(s)", unique_vals, key=f"f_val_{i}")

                    if st.button("➕ Add Filter", key=f"add_filt_{i}"):
                        if f_col_selection != "-- None / Select Field --" and f_val_selections:
                            cell["filters"].append({"column": f_col_selection, "values": f_val_selections})
                            st.rerun()

                    if cell["filters"]:
                        st.write("**Active Added Filters:**")
                        for filt_idx, filt in enumerate(cell["filters"]):
                            fl_c1, fl_c2 = st.columns([4, 1])
                            fl_c1.text(f"{filt['column']} IN {filt['values']}")
                            if fl_c2.button("❌", key=f"del_filt_{i}_{filt_idx}"):
                                cell["filters"].pop(filt_idx)
                                st.rerun()

                    if st.button("▶ Run View", key=f"run_bi_view_{i}"):
                        try:
                            filtered_df = df.copy()
                            
                            # 1. Apply saved filters in cell["filters"]
                            for filt in cell["filters"]:
                                col_name = filt["column"]
                                target_vals = [str(v).strip() for v in filt["values"]]
                                filtered_df = filtered_df[filtered_df[col_name].astype(str).str.strip().isin(target_vals)]

                            # 2. ALSO apply current active multiselect options if not explicitly added yet
                            if f_col_selection != "-- None / Select Field --" and f_val_selections:
                                target_vals = [str(v).strip() for v in f_val_selections]
                                filtered_df = filtered_df[filtered_df[f_col_selection].astype(str).str.strip().isin(target_vals)]

                            # Aggregate if X and Y axes are defined
                            if cell['viz_type'] != "Table" and cell['x_col'] and cell['y_col']:
                                res_df = filtered_df.groupby(cell['x_col'], as_index=False)[cell['y_col']].sum()
                            else:
                                res_df = filtered_df
                            
                            cell['output_data'] = res_df
                            st.success(f"Updated View! ({len(res_df)} rows match)")
                        except Exception as e:
                            st.error(f"Calculation Error: {e}")

                if st.button("🗑️ Delete Cell", key=f"del_{i}"):
                    st.session_state.cells.pop(i)
                    st.rerun()

    with col_right:
        st.subheader("🗠 Right Panel Dashboard Canvas")
        
        if st.session_state.cells:
            for i, cell in enumerate(st.session_state.cells):
                with st.container(border=True):
                    st.caption(f"Output Card — Cell {i} ({cell['type']})")
                    
                    if "Markdown" in cell['type']:
                        if cell.get('output_data'):
                            st.markdown(cell['output_data'])
                        elif cell.get('content'):
                            st.markdown(cell['content'])
                        else:
                            st.info("Write text/headings in the left editor.")
                            
                    elif cell['output_data'] is not None:
                        res = cell['output_data']
                        v_type = cell['viz_type']
                        
                        if v_type == "Table" or not isinstance(res, pd.DataFrame):
                            st.dataframe(res, use_container_width=True)
                        else:
                            x_col = cell.get('x_col')
                            y_col = cell.get('y_col')
                            
                            if not x_col or x_col not in res.columns:
                                x_col = res.columns[0]
                            if not y_col or y_col not in res.columns:
                                y_col = res.columns[1] if len(res.columns) > 1 else res.columns[0]
                            
                            fig = None
                            if v_type == "Bar Chart":
                                fig = px.bar(res, x=x_col, y=y_col, template="plotly_dark")
                            elif v_type == "Line Chart":
                                fig = px.line(res, x=x_col, y=y_col, markers=True, template="plotly_dark")
                            elif v_type == "Scatter Plot":
                                fig = px.scatter(res, x=x_col, y=y_col, template="plotly_dark")
                            elif v_type == "Pie Chart":
                                fig = px.pie(res, names=x_col, values=y_col, template="plotly_dark")
                            elif v_type == "Area Chart":
                                fig = px.area(res, x=x_col, y=y_col, template="plotly_dark")
                                
                            if fig:
                                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                                st.plotly_chart(fig, use_container_width=True, key=f"plotly_{i}")
                    else:
                        st.info("Run query or view options on left panel to view visual output here.")
        else:
            st.info("Add cells from the left panel to populate the canvas.")
else:
    st.info("← Please load a Project Bundle or a standalone dataset from the sidebar to get started.")