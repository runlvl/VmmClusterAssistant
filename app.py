import streamlit as st
import os
import sys
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from pathlib import Path
import base64
import json

# Import navigation utilities
from utils.navigation import go_to_installation

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

# Import utility modules
from utils.dependency_checker import check_dependencies
from utils.system_checker import check_system_requirements
from data.best_practices import get_best_practices
from data.requirements import get_hardware_requirements, get_software_requirements

# App configuration
st.set_page_config(
    page_title="Hyper-V Cluster Implementation Tool - Bechtle Austria GmbH",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to display the logo
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def set_header():
    logo_path = "assets/bechtle_logo.png"
    logo_base64 = get_base64_of_image(logo_path)
    
    # Set the logo and header text with improved formatting
    header_html = f"""
    <style>
        .header-container {{
            display: flex;
            align-items: flex-end; /* Align items to the bottom */
            padding-bottom: 1rem;
            margin-top: 0.5rem;
        }}
        .logo-container {{
            margin-right: 12px;
            line-height: 0; /* Remove any line-height spacing */
        }}
        .logo-image {{
            height: 50px;
            display: block; /* Remove any inline spacing */
        }}
        .header-text {{
            display: inline-block;
            line-height: 1;
            padding-bottom: 4px; /* Increased to move text up relative to logo */
        }}
        .header-title {{
            color: #1C5631;
            font-size: 22px;
            font-weight: 600;
            margin: 0;
            white-space: nowrap;
            padding-left: 5px;
        }}
    </style>
    <div class="header-container">
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" class="logo-image">
        </div>
        <div class="header-text">
            <div class="header-title"><span style="font-size: 30px; font-weight: 700;">Professional Services</span> | Datacenter & Endpoint</div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# Initialize session state for progress tracking and UI preferences
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0

if 'completed_steps' not in st.session_state:
    st.session_state.completed_steps = set()

# Add settings in sidebar
with st.sidebar:
    st.markdown("### Einstellungen")
    dark_mode = st.toggle("Dunkelmodus", value=False, key="dark_mode")
    
    # Apply custom styles based on theme
    if dark_mode:
        st.markdown("""
        <style>
        /* Dunkelgraue Farbpalette für den Dark Mode */
        :root {
            --background-main: #1E1E1E;
            --background-secondary: #2D2D2D;
            --background-tertiary: #3A3A3A;
            --text-primary: #E0E0E0;
            --text-secondary: #B0B0B0;
            --accent-color: #2E7D4B;
            --border-color: #4D4D4D;
            --hover-bg: #3E3E3E;
        }
        
        /* Haupthintergrund */
        .stApp {
            background-color: var(--background-main);
            color: var(--text-primary);
        }
        .block-container {
            background-color: var(--background-main);
        }
        
        /* Text-Elemente */
        .stMarkdown, .stText, .stCode, p, span, label, div, h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
        }
        .css-145kmo2, .css-zt5igj, .css-erpbzb, .css-und85c, .css-184tjsw p, .css-1n76uvr, .css-qehhe6, .css-1offfwp {
            color: var(--text-primary) !important;
        }
        
        /* Tabs und Navigation */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--background-secondary);
        }
        .stTabs [data-baseweb="tab"] {
            color: var(--text-primary);
        }
        
        /* Tabellen */
        table {
            color: var(--text-primary) !important;
        }
        th {
            color: var(--text-primary) !important;
            background-color: var(--background-tertiary) !important;
            font-weight: bold !important;
        }
        td {
            color: var(--text-primary) !important;
            background-color: var(--background-secondary) !important;
        }
        .stDataFrame, .dataframe {
            color: var(--text-primary) !important;
        }
        
        /* Tabellenzellen */
        .st-co, .st-cx, .st-cy {
            background-color: var(--background-secondary) !important;
            color: var(--text-primary) !important;
        }
        .st-c0, .st-c1, .st-c2, .st-c3, .st-c4, .st-c5, .st-c6, .st-c7, .st-c8, .st-c9, .st-ca, .st-cb, .st-cc, .st-cd, .st-ce, .st-cf, .st-cg, .st-ch, .st-ci, .st-cj, .st-ck, .st-cl, .st-cm, .st-cn, .st-co, .st-cp, .st-cq, .st-cr, .st-cs, .st-ct, .st-cu, .st-cv, .st-cw, .st-cx {
            background-color: var(--background-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        /* Expander und Alerts */
        .streamlit-expanderHeader {
            color: var(--text-primary) !important;
            background-color: var(--background-secondary) !important;
            border-color: var(--border-color) !important;
        }
        .streamlit-expanderContent {
            color: var(--text-primary) !important;
            background-color: var(--background-secondary) !important;
            border-color: var(--border-color) !important;
        }
        .stAlert {
            background-color: var(--background-secondary) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }
        .stAlert > div {
            color: var(--text-primary) !important;
        }
        
        /* Info-Boxen */
        .stInfo {
            background-color: rgba(46, 125, 75, 0.2) !important;
            color: var(--text-primary) !important;
        }
        .stSuccess {
            background-color: rgba(46, 125, 75, 0.2) !important;
        }
        .stWarning {
            background-color: rgba(255, 182, 0, 0.2) !important;
        }
        .stError {
            background-color: rgba(255, 0, 0, 0.2) !important;
        }
        
        /* Buttons und Formularelemente */
        button {
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
            background-color: var(--background-tertiary) !important;
        }
        button:hover {
            background-color: var(--hover-bg) !important;
        }
        select, input, textarea {
            color: var(--text-primary) !important;
            background-color: var(--background-tertiary) !important;
            border-color: var(--border-color) !important;
        }
        .stSelectbox > div, .stMultiselect > div {
            background-color: var(--background-tertiary) !important;
            border-color: var(--border-color) !important;
        }
        
        /* Checkboxen und Radio-Buttons */
        .stCheckbox > div, .stRadio > div {
            color: var(--text-primary) !important;
        }
        
        /* Slider */
        .stSlider > div {
            color: var(--text-primary) !important;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--background-secondary) !important;
            border-right: 1px solid var(--border-color) !important;
        }
        
        /* Container mit Rahmen */
        [data-testid="stVerticalBlock"] > div > div[style*="border"] {
            border-color: var(--border-color) !important;
            background-color: var(--background-secondary) !important;
        }
        
        /* Optionaler Bechtle-Akzent für ausgewählte Elemente */
        .stButton > button[data-baseweb="button"]:active {
            background-color: var(--accent-color) !important;
        }
        .stProgress > div > div > div > div {
            background-color: var(--accent-color) !important;
        }
        </style>
        """, unsafe_allow_html=True)

# Call the header function
set_header()

if 'configuration' not in st.session_state:
    st.session_state.configuration = {
        "deployment_type": "hyperv", # Default to Hyper-V only deployment
        "hardware": {},
        "software": {},
        "network": {},
        "storage": {},
        "security": {},
        "ha": {},
        "backup": {},
        "roles": {},
        "monitoring": {}
    }
    
# Initialize navigation buttons state
for i in range(7):  # For all possible steps
    if f"goto_{i}" not in st.session_state:
        st.session_state[f"goto_{i}"] = False
        
# Helper function for navigation
def set_navigation_target(target):
    st.session_state.current_step = target

# Initialize deployment type if not set
if "deployment_type" not in st.session_state.configuration:
    st.session_state.configuration["deployment_type"] = "hyperv"

# Define base implementation steps for Hyper-V
base_implementation_steps = [
    "Introduction",
    "Installation",
    "Hardware Requirements",
    "Software Requirements",
    "Network Configuration",
    "Storage Configuration",
    "Generate Implementation Documentation (Final Step)"
]

# Define SCVMM-specific steps (empty because these steps are removed)
scvmm_steps = []

# Initialize implementation steps based on deployment type
deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")

# Store implementation steps in session state to allow dynamic updating
if "implementation_steps" not in st.session_state:
    if deployment_type == "hyperv":
        st.session_state.implementation_steps = base_implementation_steps.copy()
    else:
        # Insert SCVMM-specific steps before the final step
        st.session_state.implementation_steps = base_implementation_steps[:-1] + scvmm_steps + [base_implementation_steps[-1]]

# Use the steps from session state
implementation_steps = st.session_state.implementation_steps

# Sidebar
with st.sidebar:
    st.title("Hyper-V Cluster Implementation")
    st.caption("Bechtle Austria GmbH")
    
    # Add navigation helper functions to session state for direct access
    if "navigate_to" not in st.session_state:
        def navigate_to(step_index):
            st.session_state.current_step = step_index
            st.rerun()
        st.session_state.navigate_to = navigate_to
    
    # Display progress based on current step rather than completed steps
    # This ensures the progress bar matches navigation position
    current_progress = st.session_state.current_step / (len(implementation_steps) - 1) if len(implementation_steps) > 1 else 0
    st.progress(current_progress)
    progress_percentage = current_progress * 100
    st.caption(f"Implementation Progress: {progress_percentage:.1f}%")
    
    # Navigation
    selected_step = option_menu(
        "Implementation Steps",
        implementation_steps,
        icons=[
            "info-circle", "download", "cpu", "gear", "diagram-3", "hdd", 
            "shield-lock", "file-earmark-text"
        ],
        menu_icon="list",
        default_index=st.session_state.current_step,
    )
    
    if selected_step != implementation_steps[st.session_state.current_step]:
        st.session_state.current_step = implementation_steps.index(selected_step)
        st.rerun()
    
    # System check button
    if st.button("Run System Check"):
        with st.spinner("Checking system requirements..."):
            system_status = check_system_requirements()
            if system_status["status"]:
                st.success("✅ System meets requirements for running this tool")
            else:
                st.error(f"❌ System check failed: {system_status['message']}")

    # Dependency check button
    if st.button("Check Dependencies"):
        with st.spinner("Checking dependencies..."):
            dependency_status = check_dependencies()
            if dependency_status["status"]:
                st.success("✅ All dependencies are installed")
            else:
                st.error(f"❌ Missing dependencies: {', '.join(dependency_status['missing'])}")
                st.info("Please install the missing dependencies to continue")

# Main content area
def render_introduction():
    st.title("Hyper-V Cluster Implementation Tool")
    
    # Add deployment type selection
    st.header("Select Deployment Type")
    
    deployment_options = {
        "hyperv": "Hyper-V Cluster Only",
        "scvmm": "Hyper-V Cluster with System Center VMM"
    }
    
    # Create columns for the deployment type selection
    col1, col2 = st.columns(2)
    
    # Check current deployment type
    current_type = st.session_state.configuration.get("deployment_type", "hyperv")
    hyperv_selected_style = "background-color: #1C5631; color: white; padding: 10px;" if current_type == "hyperv" else ""
    scvmm_selected_style = "background-color: #1C5631; color: white; padding: 10px;" if current_type == "scvmm" else ""
    
    with col1:
        with st.container(border=True):
            st.markdown(f"<div style='{hyperv_selected_style}'>### Hyper-V Cluster Only</div>", unsafe_allow_html=True)
            st.markdown("""
            - **Empfohlener Standard** für die meisten Einsatzszenarien
            - Einfache Implementierung mit reduzierter Komplexität
            - Grundlegende Cluster-Funktionalität
            - Schnellere Bereitstellung
            - Keine zusätzlichen Lizenzkosten für SCVMM
            """)
            hyperv_selected = st.button("Hyper-V Cluster auswählen", key="hyperv_select", use_container_width=True)
    
    with col2:
        with st.container(border=True):
            st.markdown(f"<div style='{scvmm_selected_style}'>### Mit System Center VMM</div>", unsafe_allow_html=True)
            st.markdown("""
            - Erweiterte Management-Funktionen
            - Zentralisierte Verwaltung
            - Zusätzliche Komplexität
            - Benötigt SQL Server und weitere Komponenten
            - Höhere Anforderungen an Ressourcen und Wartung
            """)
            scvmm_selected = st.button("Mit SCVMM auswählen", key="scvmm_select", use_container_width=True)
    
    # Handle deployment type selection and update menu
    if hyperv_selected:
        st.session_state.configuration["deployment_type"] = "hyperv"
        # Update implementation steps based on new deployment type
        st.session_state.implementation_steps = base_implementation_steps.copy()
        st.success("✅ Hyper-V Cluster Only deployment selected")
        # Force reload to update sidebar menu
        st.rerun()
    
    if scvmm_selected:
        st.session_state.configuration["deployment_type"] = "scvmm"
        # Update implementation steps based on new deployment type
        st.session_state.implementation_steps = base_implementation_steps[:-1] + scvmm_steps + [base_implementation_steps[-1]]
        st.success("✅ Hyper-V Cluster with SCVMM deployment selected")
        # Force reload to update sidebar menu
        st.rerun()
    
    # Display current selection
    current_type = st.session_state.configuration.get("deployment_type", "hyperv")
    st.markdown(f"**Current selection:** {deployment_options[current_type]}")
    
    # Welcome message based on deployment type
    if current_type == "hyperv":
        welcome_title = "Welcome to the Hyper-V Cluster Implementation Tool!"
        welcome_desc = "This wizard will guide you through the process of setting up a Hyper-V cluster with best practices, automated validation, and comprehensive documentation."
    else:
        welcome_title = "Welcome to the Hyper-V Cluster with SCVMM Implementation Tool!"
        welcome_desc = "This wizard will guide you through the process of setting up a Hyper-V cluster with System Center Virtual Machine Manager (SCVMM), including best practices, automated validation, and comprehensive documentation."
    
    st.markdown(f"""
    ## {welcome_title}
    
    {welcome_desc}
    
    ### Key Features:
    - Step-by-step implementation guidance
    - Automatic validation of requirements
    - Best practice recommendations
    - Security and high availability configuration
    - Comprehensive documentation generation
    
    ### How to Use This Tool:
    1. Navigate through each step using the sidebar menu
    2. Complete the required information at each stage
    3. The tool will validate your inputs and provide feedback
    4. After completing all steps, you'll receive documentation and implementation scripts
    
    Let's begin by going through each step in order, starting with the "Installation" step.
    """)
    
    # Display overview of cluster architecture based on deployment type
    current_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    if current_type == "hyperv":
        st.subheader("Hyper-V Cluster Architecture Overview")
    else:
        st.subheader("Hyper-V Cluster with SCVMM Architecture Overview")
    
    # Create a simple graph to visualize the architecture
    G = nx.Graph()
    
    # Add nodes
    if current_type == "hyperv":
        # Hyper-V only deployment
        nodes = ["Hyper-V Host 1", "Hyper-V Host 2", 
                "Shared Storage", "Management Network", "VM Network", "Migration Network"]
    else:
        # SCVMM deployment
        nodes = ["VMM Server", "SQL Server", "Hyper-V Host 1", "Hyper-V Host 2", 
                "Shared Storage", "Management Network", "VM Network", "Migration Network"]
    
    for node in nodes:
        G.add_node(node)
    
    # Add edges
    edges = []
    
    # Common edges for both deployment types
    common_edges = [
        ("Hyper-V Host 1", "Management Network"),
        ("Hyper-V Host 2", "Management Network"),
        ("Hyper-V Host 1", "VM Network"),
        ("Hyper-V Host 2", "VM Network"),
        ("Hyper-V Host 1", "Migration Network"),
        ("Hyper-V Host 2", "Migration Network"),
        ("Hyper-V Host 1", "Shared Storage"),
        ("Hyper-V Host 2", "Shared Storage")
    ]
    
    edges.extend(common_edges)
    
    # Add SCVMM-specific edges if applicable
    if current_type == "scvmm":
        scvmm_edges = [
            ("VMM Server", "SQL Server"),
            ("VMM Server", "Management Network"),
            ("SQL Server", "Management Network")
        ]
        edges.extend(scvmm_edges)
    
    G.add_edges_from(edges)
    
    # Create positions for nodes
    # Common positions for both deployment types
    pos = {
        "Hyper-V Host 1": [0, 0],
        "Hyper-V Host 2": [2, 0],
        "Shared Storage": [1, -1],
        "Management Network": [1, 1.5 if current_type == "hyperv" else 3],
        "VM Network": [3, 1],
        "Migration Network": [-1, 1]
    }
    
    # Add SCVMM-specific positions if applicable
    if current_type == "scvmm":
        scvmm_pos = {
            "VMM Server": [0, 2],
            "SQL Server": [2, 2]
        }
        pos.update(scvmm_pos)
    
    # Create edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            size=30,
            color='#007BFF',
            line_width=2))
    
    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=500,
                       title=f"{'Standard' if current_type == 'hyperv' else 'Advanced with SCVMM'} Cluster Configuration",
                       plot_bgcolor='rgba(240,240,240,0.3)',
                       paper_bgcolor='rgba(0,0,0,0)',
                   ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Best Practices Summary
    current_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    if current_type == "hyperv":
        st.subheader("Hyper-V Cluster Implementation Best Practices")
    else:
        st.subheader("Hyper-V Cluster with SCVMM Implementation Best Practices")
    
    best_practices = get_best_practices()
    categories = list(best_practices.keys())
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(categories)
    
    with tab1:
        for practice in best_practices[categories[0]]:
            st.markdown(f"- {practice}")
    
    with tab2:
        for practice in best_practices[categories[1]]:
            st.markdown(f"- {practice}")
    
    with tab3:
        for practice in best_practices[categories[2]]:
            st.markdown(f"- {practice}")
    
    with tab4:
        for practice in best_practices[categories[3]]:
            st.markdown(f"- {practice}")
    
    with tab5:
        for practice in best_practices[categories[4]]:
            st.markdown(f"- {practice}")
    
    # Create simple navigation buttons with session state
    st.markdown("---")
    
    # Streamlit buttons with dedicated keys
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        next_button = st.button("→ Installation Guide", use_container_width=True)
        if next_button:
            st.session_state.current_step = 1
            st.rerun()

# Main content renderer
if st.session_state.current_step == 0:
    render_introduction()
elif st.session_state.current_step == 1:
    # Import and render at runtime to avoid circular imports
    from modules.installation import render_installation_documentation
    render_installation_documentation()
elif st.session_state.current_step == 2:
    from modules.hardware_requirements import render_hardware_requirements
    render_hardware_requirements()
elif st.session_state.current_step == 3:
    from modules.software_requirements import render_software_requirements
    render_software_requirements()
elif st.session_state.current_step == 4:
    from modules.network_configuration import render_network_configuration
    render_network_configuration()
elif st.session_state.current_step == 5:
    from modules.storage_configuration import render_storage_configuration
    render_storage_configuration()
elif st.session_state.current_step == 6:
    from modules.documentation import render_documentation
    render_documentation()

# Footer
st.markdown("---")
st.caption("VMM Cluster Implementation Tool • © 2025 Bechtle Austria GmbH • v1.0.0")
