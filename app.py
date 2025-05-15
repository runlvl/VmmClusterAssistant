import streamlit as st
import os
import sys
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

# Import utility modules
from utils.dependency_checker import check_dependencies
from utils.system_checker import check_system_requirements
from data.best_practices import get_best_practices
from data.requirements import get_hardware_requirements, get_software_requirements

# App configuration
st.set_page_config(
    page_title="VMM Cluster Implementation Tool",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for progress tracking
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0

if 'completed_steps' not in st.session_state:
    st.session_state.completed_steps = set()

if 'configuration' not in st.session_state:
    st.session_state.configuration = {
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

# Define implementation steps
implementation_steps = [
    "Introduction",
    "Installation",
    "Hardware Requirements",
    "Software Requirements",
    "Network Configuration",
    "Storage Configuration",
    "Security Settings",
    "High Availability",
    "Backup & Restore",
    "Roles & Permissions",
    "Monitoring",
    "Documentation"
]

# Sidebar
with st.sidebar:
    st.title("VMM Cluster Implementation")
    
    # Display progress
    progress_percentage = len(st.session_state.completed_steps) / (len(implementation_steps) - 1) * 100 if len(implementation_steps) > 1 else 0
    st.progress(progress_percentage / 100)
    st.caption(f"Implementation Progress: {progress_percentage:.1f}%")
    
    # Navigation
    selected_step = option_menu(
        "Implementation Steps",
        implementation_steps,
        icons=[
            "info-circle", "download", "cpu", "gear", "diagram-3", "hdd", 
            "shield-lock", "arrow-repeat", "archive", "people", 
            "graph-up", "file-earmark-text"
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
    st.title("VMM Cluster Implementation Tool")
    st.markdown("""
    ## Welcome to the VMM Cluster Implementation Tool!
    
    This wizard will guide you through the process of setting up a System Center Virtual Machine Manager (VMM) cluster
    with best practices, automated validation, and comprehensive documentation.
    
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
    
    Let's begin by clicking on the "Hardware Requirements" step in the sidebar.
    """)
    
    # Display overview of VMM cluster architecture
    st.subheader("VMM Cluster Architecture Overview")
    
    # Create a simple graph to visualize VMM architecture
    G = nx.Graph()
    
    # Add nodes
    nodes = ["VMM Server", "SQL Server", "Hyper-V Host 1", "Hyper-V Host 2", 
             "Shared Storage", "Management Network", "VM Network", "Migration Network"]
    
    for node in nodes:
        G.add_node(node)
    
    # Add edges
    edges = [
        ("VMM Server", "SQL Server"),
        ("VMM Server", "Management Network"),
        ("SQL Server", "Management Network"),
        ("Hyper-V Host 1", "Management Network"),
        ("Hyper-V Host 2", "Management Network"),
        ("Hyper-V Host 1", "VM Network"),
        ("Hyper-V Host 2", "VM Network"),
        ("Hyper-V Host 1", "Migration Network"),
        ("Hyper-V Host 2", "Migration Network"),
        ("Hyper-V Host 1", "Shared Storage"),
        ("Hyper-V Host 2", "Shared Storage")
    ]
    
    G.add_edges_from(edges)
    
    # Create positions for nodes
    pos = {
        "VMM Server": [0, 2],
        "SQL Server": [2, 2],
        "Hyper-V Host 1": [0, 0],
        "Hyper-V Host 2": [2, 0],
        "Shared Storage": [1, -1],
        "Management Network": [1, 3],
        "VM Network": [3, 1],
        "Migration Network": [-1, 1]
    }
    
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
                       plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)',
                   ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Best Practices Summary
    st.subheader("VMM Cluster Implementation Best Practices")
    
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
    
    # Buttons for next steps
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Installation Guide", key="next_to_installation"):
            st.session_state.current_step = 1
            st.rerun()
    with col2:
        if st.button("Proceed to Hardware Requirements", key="next_to_hardware"):
            st.session_state.current_step = 2
            st.rerun()

# Main content renderer
if st.session_state.current_step == 0:
    render_introduction()
elif st.session_state.current_step == 1:
    # Import and render at runtime to avoid circular imports
    from pages.installation import render_installation_documentation
    render_installation_documentation()
elif st.session_state.current_step == 2:
    from pages.hardware_requirements import render_hardware_requirements
    render_hardware_requirements()
elif st.session_state.current_step == 3:
    from pages.software_requirements import render_software_requirements
    render_software_requirements()
elif st.session_state.current_step == 4:
    from pages.network_configuration import render_network_configuration
    render_network_configuration()
elif st.session_state.current_step == 5:
    from pages.storage_configuration import render_storage_configuration
    render_storage_configuration()
elif st.session_state.current_step == 6:
    from pages.security_settings import render_security_settings
    render_security_settings()
elif st.session_state.current_step == 7:
    from pages.high_availability import render_high_availability
    render_high_availability()
elif st.session_state.current_step == 8:
    from pages.backup_restore import render_backup_restore
    render_backup_restore()
elif st.session_state.current_step == 9:
    from pages.roles_permissions import render_roles_permissions
    render_roles_permissions()
elif st.session_state.current_step == 10:
    from pages.monitoring import render_monitoring
    render_monitoring()
elif st.session_state.current_step == 11:
    from pages.documentation import render_documentation
    render_documentation()

# Footer
st.markdown("---")
st.caption("VMM Cluster Implementation Tool • © 2023 • v1.0.0")
