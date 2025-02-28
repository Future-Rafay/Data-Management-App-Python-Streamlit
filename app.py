# Imports
import streamlit as st
import pandas as pd
import os
import plotly.express as px
from io import BytesIO
from datetime import datetime

# Page configuration (must be first)
st.set_page_config(
    page_title='Data Management Pro',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS
st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    .stDownloadButton button {background-color: #4CAF50!important;}
    div[data-baseweb="select"] > div {border-color: #4CAF50!important;}
    .st-emotion-cache-18ni7ap {background-color: #2c3e50;}
    .message {padding: 10px; margin: 10px 0; border-radius: 5px;}
    .success {background-color: #d4edda; color: #155724;}
    .error {background-color: #f8d7da; color: #721c24;}
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if 'original_data' not in st.session_state:
    st.session_state.original_data = None
if 'data_frame' not in st.session_state:
    st.session_state.data_frame = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Display messages
def show_messages():
    if st.session_state.messages:
        for msg in st.session_state.messages:
            st.markdown(f'<div class="message {msg["type"]}">📢 {msg["content"]}</div>', 
                       unsafe_allow_html=True)
        # Clear messages after 5 seconds
        if (datetime.now() - st.session_state.last_update).seconds > 5:
            st.session_state.messages = []
            st.session_state.last_update = datetime.now()
            st.rerun()

# App Title
st.title('📊 Data Management Pro')
st.markdown("**All-in-One Data Processing Solution**  \n*Clean, Analyze, and Convert Data Effortlessly*")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Controls")
    data_source = st.radio("Data Source", ["Upload File", "Sample Data"])
    
    if data_source == "Upload File":
        uploaded_file = st.file_uploader("Choose files", 
            type=['csv','xlsx'], 
            accept_multiple_files=False)
    else:
        uploaded_file = None
        
    st.markdown("---")
    if st.button("Clear All Cache"):
        st.cache_data.clear()
        st.session_state.clear()
        st.rerun()

# Data Loading Function
def load_data():
    try:
        if data_source == "Sample Data":
            df = pd.DataFrame({
                'Date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
                'Sales': [200, 250, None, 300, 400, 250, 200, 500, None, 350],
                'Region': ['North', 'North', 'South', 'East', 'East', 'North', 'North', 'West', 'South', 'East'],
                'Temperature': [28.5, 30.1, 32.3, 29.8, 31.2, 30.1, 28.5, 27.9, 32.3, 29.8]
            })
            st.session_state.messages.append({
                'type': 'success',
                'content': 'Loaded sample dataset'
            })
        elif uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.messages.append({
                'type': 'success',
                'content': f'Successfully loaded {uploaded_file.name}'
            })
        else:
            return None
        
        st.session_state.original_data = df.copy()
        st.session_state.data_frame = df.copy()
        return df
    except Exception as e:
        st.session_state.messages.append({
            'type': 'error',
            'content': f'Error loading data: {str(e)}'
        })
        return None

# Load Data
if st.session_state.data_frame is None:
    load_data()

# Main App Logic
if st.session_state.data_frame is not None:
    show_messages()
    
    # File Summary Section
    with st.expander("📄 Dataset Overview", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", st.session_state.data_frame.shape[0])
        col2.metric("Total Columns", st.session_state.data_frame.shape[1])
        col3.metric("Missing Values", st.session_state.data_frame.isna().sum().sum())

    # Data Preview Tabs
    tab1, tab2, tab3 = st.tabs(["First Look", "Quick Stats", "Full Data"])
    with tab1:
        st.dataframe(st.session_state.data_frame.head(), use_container_width=True)
    with tab2:
        st.write("**Data Types:**")
        st.write(st.session_state.data_frame.dtypes)
        st.write("**Basic Statistics:**")
        st.write(st.session_state.data_frame.describe())
    with tab3:
        st.dataframe(st.session_state.data_frame, use_container_width=True)

    # Data Cleaning Tools
    with st.expander("🧹 Data Cleaning", expanded=False):
        clean_col1, clean_col2 = st.columns(2)
        
        with clean_col1:
            st.subheader("Data Quality")
            if st.button("Remove Duplicates"):
                try:
                    initial = st.session_state.data_frame.shape[0]
                    st.session_state.data_frame = st.session_state.data_frame.drop_duplicates()
                    removed = initial - st.session_state.data_frame.shape[0]
                    st.session_state.messages.append({
                        'type': 'success',
                        'content': f'Removed {removed} duplicates'
                    })
                except Exception as e:
                    st.session_state.messages.append({
                        'type': 'error',
                        'content': f'Error removing duplicates: {str(e)}'
                    })
           

        with clean_col2:
            st.subheader("Missing Values Handling")
            na_action = st.selectbox("Handle Missing Values", 
                ["Keep", "Drop Rows", "Fill with 0", "Fill with Mean"])
            
            if st.button("Apply Missing Values Handling"):
                try:
                    if na_action == "Drop Rows":
                        st.session_state.data_frame = st.session_state.data_frame.dropna()
                    elif na_action == "Fill with 0":
                        st.session_state.data_frame = st.session_state.data_frame.fillna(0)
                    elif na_action == "Fill with Mean":
                        st.session_state.data_frame = st.session_state.data_frame.fillna(
                            st.session_state.data_frame.mean(numeric_only=True))
                    st.session_state.messages.append({
                        'type': 'success',
                        'content': f'Applied missing values handling: {na_action}'
                    })
                except Exception as e:
                    st.session_state.messages.append({
                        'type': 'error',
                        'content': f'Error handling missing values: {str(e)}'
                    })

    # Interactive Data Editor Section
    with st.expander("✏️ Edit Data", expanded=False):
        st.subheader("Interactive Data Editor")
        
        edit_col1, edit_col2 = st.columns(2)
        
        with edit_col1:
            new_col = st.text_input("Add new column")
            if st.button("Add Column") and new_col:
                try:
                    if new_col not in st.session_state.data_frame.columns:
                        st.session_state.data_frame[new_col] = ""
                        st.session_state.messages.append({
                            'type': 'success',
                            'content': f'Added column: {new_col}'
                        })
                    else:
                        st.session_state.messages.append({
                            'type': 'error',
                            'content': 'Column already exists!'
                        })
                except Exception as e:
                    st.session_state.messages.append({
                        'type': 'error',
                        'content': f'Error adding column: {str(e)}'
                    })
        
        with edit_col2:
            del_col = st.selectbox("Delete column", st.session_state.data_frame.columns)
            if st.button("Delete Column"):
                try:
                    st.session_state.data_frame = st.session_state.data_frame.drop(columns=del_col)
                    st.session_state.messages.append({
                        'type': 'success',
                        'content': f'Deleted column: {del_col}'
                    })
                except Exception as e:
                    st.session_state.messages.append({
                        'type': 'error',
                        'content': f'Error deleting column: {str(e)}'
                    })

        # Editable Data Grid
        st.info("Double-click cells to edit. Press Ctrl+Enter to save changes")
        edited_df = st.data_editor(
            st.session_state.data_frame,
            num_rows="dynamic",
            key="data_editor",
            height=400
        )
        
        # Update dataframe with changes
        if not edited_df.equals(st.session_state.data_frame):
            st.session_state.data_frame = edited_df.copy()
            st.session_state.messages.append({
                'type': 'success',
                'content': 'Data changes saved!'
            })
            st.rerun()

        # Row Management
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Add Empty Row"):
                try:
                    st.session_state.data_frame.loc[len(st.session_state.data_frame)] = [""]*len(st.session_state.data_frame.columns)
                    st.session_state.messages.append({
                        'type': 'success',
                        'content': 'Added empty row'
                    })
                except Exception as e:
                    st.session_state.messages.append({
                        'type': 'error',
                        'content': f'Error adding row: {str(e)}'
                    })
        with col2:
            if st.button("❌ Delete Selected Rows"):
                try:
                    selected = st.session_state.data_editor["edited_rows"]
                    if selected:
                        st.session_state.data_frame = st.session_state.data_frame.drop(index=list(selected.keys()))
                        st.session_state.messages.append({
                            'type': 'success',
                            'content': f'Deleted {len(selected)} rows'
                        })
                except Exception as e:
                    st.session_state.messages.append({
                        'type': 'error',
                        'content': f'Error deleting rows: {str(e)}'
                    })
        with col3:
            if st.button("🔄 Reset to Original"):
                try:
                    st.session_state.data_frame = st.session_state.original_data.copy()
                    st.session_state.messages.append({
                        'type': 'success',
                        'content': 'Data reset to original state'
                    })
                except Exception as e:
                    st.session_state.messages.append({
                        'type': 'error',
                        'content': f'Error resetting data: {str(e)}'
                    })

    # Enhanced Data Visualization
    with st.expander("📈 Visual Analysis", expanded=False):
        try:
            numeric_cols = st.session_state.data_frame.select_dtypes(include='number').columns.tolist()
            date_cols = st.session_state.data_frame.select_dtypes(include='datetime').columns.tolist()
            
            chart_col1, chart_col2 = st.columns([1, 3])
            with chart_col1:
                chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Scatter", "Histogram", "Box"])
                x_axis = st.selectbox("X Axis", [''] + date_cols + numeric_cols + list(st.session_state.data_frame.columns))
                y_axis = st.multiselect("Y Axis", numeric_cols)
                color_dim = st.selectbox("Color", ['None'] + list(st.session_state.data_frame.columns))
                
                if chart_type in ['Scatter', 'Box']:
                    hover_data = st.multiselect("Hover Data", st.session_state.data_frame.columns)
                else:
                    hover_data = None
                    
            with chart_col2:
                if y_axis:
                    try:
                        if chart_type == "Line":
                            fig = px.line(st.session_state.data_frame, x=x_axis, y=y_axis, 
                                        color=None if color_dim == 'None' else color_dim,
                                        hover_data=hover_data)
                        elif chart_type == "Bar":
                            fig = px.bar(st.session_state.data_frame, x=x_axis, y=y_axis, 
                                        color=None if color_dim == 'None' else color_dim,
                                        barmode='group')
                        elif chart_type == "Scatter":
                            fig = px.scatter(st.session_state.data_frame, x=x_axis, y=y_axis, 
                                           color=None if color_dim == 'None' else color_dim,
                                           hover_data=hover_data)
                        elif chart_type == "Histogram":
                            fig = px.histogram(st.session_state.data_frame, x=x_axis, y=y_axis, 
                                              color=None if color_dim == 'None' else color_dim)
                        elif chart_type == "Box":
                            fig = px.box(st.session_state.data_frame, x=x_axis, y=y_axis, 
                                        color=None if color_dim == 'None' else color_dim)
                            
                        fig.update_layout(
                            title=f"{chart_type} Chart",
                            xaxis_title=x_axis if x_axis else '',
                            yaxis_title=', '.join(y_axis) if y_axis else '',
                            legend_title=color_dim if color_dim != 'None' else None
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Chart Error: {str(e)}")
                else:
                    st.info("Select at least one Y-axis column for visualization")
        except Exception as e:
            st.error(f"Visualization setup error: {str(e)}")

    # File Conversion
    with st.expander("📤 Export Data", expanded=False):
        conv_col1, conv_col2 = st.columns(2)
        
        with conv_col1:
            export_format = st.radio("Format", 
                ["Excel", "CSV", "JSON"], horizontal=True)
        
        with conv_col2:
            custom_name = st.text_input("Custom filename", "processed_data")
        
        if st.button(f"Export as {export_format}"):
            try:
                buffer = BytesIO()
                if export_format == "Excel":
                    st.session_state.data_frame.to_excel(buffer, index=False)
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ext = ".xlsx"
                elif export_format == "CSV":
                    st.session_state.data_frame.to_csv(buffer, index=False)
                    mime = "text/csv"
                    ext = ".csv"
                else:
                    st.session_state.data_frame.to_json(buffer)
                    mime = "application/json"
                    ext = ".json"
                
                buffer.seek(0)
                st.download_button(
                    label=f"Download {ext}",
                    data=buffer,
                    file_name=f"{custom_name}{ext}",
                    mime=mime
                )
                st.session_state.messages.append({
                    'type': 'success',
                    'content': f'Exported data as {export_format}'
                })
            except Exception as e:
                st.session_state.messages.append({
                    'type': 'error',
                    'content': f'Export failed: {str(e)}'
                })

else:
    st.info("👈 Please upload a file or select sample data to begin")

st.markdown("---")  
st.markdown(
    "<div style='text-align: center; font-size: 16px;'>"
    "✨ Made with <span style='color: #FF4B4B;'>💗</span> by <b>Rafay Nadeem</b> ✨<br>"
    "🚀 Used AI Tools for Building Advanced Features"
    "</div>",
    unsafe_allow_html=True
)
