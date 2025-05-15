import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.requirements import get_hardware_requirements

def render_hardware_requirements():
    """Render the hardware requirements page."""
    st.title("Hardware Requirements")
    
    # Get hardware requirements data
    hw_requirements = get_hardware_requirements()
    
    st.write("Before implementing a VMM cluster, ensure your hardware meets or exceeds the following requirements.")
    
    # Function to update session state when requirements are confirmed
    def confirm_hardware_configuration():
        if "configuration" not in st.session_state:
            st.session_state.configuration = {}
        if "hardware" not in st.session_state.configuration:
            st.session_state.configuration["hardware"] = {}
        
        st.session_state.configuration["hardware"] = {
            "servers": servers_data,
            "host_count": host_count,
            "homogeneous": homogeneous,
            "requirements_met": True
        }
        
        if "completed_steps" not in st.session_state:
            st.session_state.completed_steps = set()
        
        st.session_state.completed_steps.add(1)  # Mark hardware step as completed
        st.session_state.current_step = 2  # Move to next step (software requirements)
        st.rerun()

    # Server requirements
    st.header("Server Requirements")
    
    # Display server requirements
    server_req_df = pd.DataFrame(hw_requirements["server_requirements"])
    st.table(server_req_df)
    
    # Storage controller requirements
    st.header("Storage Controller Requirements")
    storage_req_df = pd.DataFrame(hw_requirements["storage_requirements"])
    st.table(storage_req_df)
    
    # Network adapter requirements
    st.header("Network Requirements")
    network_req_df = pd.DataFrame(hw_requirements["network_requirements"])
    st.table(network_req_df)
    
    # Cluster node configuration
    st.header("Cluster Node Configuration")
    
    # Ask for number of hosts
    host_count = st.number_input("Number of Hyper-V Hosts", min_value=2, max_value=16, value=2, step=1,
                                help="Specify the number of Hyper-V hosts in your cluster (min: 2, max: 16)")
    
    # Ask if servers are homogeneous
    homogeneous = st.checkbox("Servers are homogeneous (recommended)", value=True, 
                             help="All servers should have identical hardware for optimal performance")
    
    # Warning for non-homogeneous servers
    if not homogeneous:
        st.warning("Using non-homogeneous servers in a cluster may lead to performance inconsistencies and management challenges.")
    
    # Server configuration
    st.subheader("Server Details")
    
    # Create server data collection
    servers_data = []
    
    for i in range(host_count):
        col1, col2 = st.columns(2)
        with st.expander(f"Server {i+1} Configuration", expanded=(i==0)):
            server_name = st.text_input(f"Server {i+1} Name", f"HyperV-Node{i+1}", key=f"server_name_{i}")
            st.caption("Server names must not exceed 15 characters")
            if len(server_name) > 15:
                st.error("Server name exceeds 15 characters. Please shorten the name.")
            
            server_model = st.text_input(f"Server {i+1} Model", key=f"server_model_{i}")
            
            col1, col2 = st.columns(2)
            with col1:
                cpu_cores = st.number_input(f"CPU Cores", min_value=2, value=4, key=f"cpu_cores_{i}")
                memory_gb = st.number_input(f"Memory (GB)", min_value=8, value=16, key=f"memory_{i}")
            
            with col2:
                nic_count = st.number_input(f"Network Adapters", min_value=2, value=4, key=f"nic_count_{i}")
                disk_gb = st.number_input(f"System Disk (GB)", min_value=100, value=200, key=f"disk_{i}")
            
            servers_data.append({
                "name": server_name,
                "model": server_model,
                "cpu_cores": cpu_cores,
                "memory_gb": memory_gb,
                "nic_count": nic_count,
                "system_disk_gb": disk_gb,
                "role": "Hyper-V Host"
            })
    
    # Add SQL and VMM servers
    with st.expander("VMM Server Configuration"):
        vmm_server_name = st.text_input("VMM Server Name", "VMM-Server")
        st.caption("Server names must not exceed 15 characters")
        if len(vmm_server_name) > 15:
            st.error("Server name exceeds 15 characters. Please shorten the name.")
        
        vmm_server_model = st.text_input("VMM Server Model")
        
        col1, col2 = st.columns(2)
        with col1:
            vmm_cpu_cores = st.number_input("CPU Cores", min_value=2, value=4, key="vmm_cpu_cores")
            vmm_memory_gb = st.number_input("Memory (GB)", min_value=8, value=16, key="vmm_memory")
        
        with col2:
            vmm_nic_count = st.number_input("Network Adapters", min_value=1, value=2, key="vmm_nic_count")
            vmm_disk_gb = st.number_input("System Disk (GB)", min_value=100, value=200, key="vmm_disk")
        
        servers_data.append({
            "name": vmm_server_name,
            "model": vmm_server_model,
            "cpu_cores": vmm_cpu_cores,
            "memory_gb": vmm_memory_gb,
            "nic_count": vmm_nic_count,
            "system_disk_gb": vmm_disk_gb,
            "role": "VMM Server"
        })
    
    with st.expander("SQL Server Configuration"):
        same_as_vmm = st.checkbox("SQL Server is on the same machine as VMM Server", value=False)
        
        if not same_as_vmm:
            sql_server_name = st.text_input("SQL Server Name", "SQL-Server")
            st.caption("Server names must not exceed 15 characters")
            if len(sql_server_name) > 15:
                st.error("Server name exceeds 15 characters. Please shorten the name.")
            
            sql_server_model = st.text_input("SQL Server Model")
            
            col1, col2 = st.columns(2)
            with col1:
                sql_cpu_cores = st.number_input("CPU Cores", min_value=2, value=4, key="sql_cpu_cores")
                sql_memory_gb = st.number_input("Memory (GB)", min_value=8, value=16, key="sql_memory")
            
            with col2:
                sql_nic_count = st.number_input("Network Adapters", min_value=1, value=2, key="sql_nic_count")
                sql_disk_gb = st.number_input("System Disk (GB)", min_value=100, value=200, key="sql_disk")
            
            servers_data.append({
                "name": sql_server_name,
                "model": sql_server_model,
                "cpu_cores": sql_cpu_cores,
                "memory_gb": sql_memory_gb,
                "nic_count": sql_nic_count,
                "system_disk_gb": sql_disk_gb,
                "role": "SQL Server"
            })
    
    # Hardware validation and visualization
    st.header("Hardware Requirements Validation")
    
    # Create a radar chart to show hardware adequacy
    categories = ['CPU Cores', 'Memory', 'Network', 'Storage']
    recommended = [4, 16, 4, 200]  # Recommended values
    
    # Calculate average values for all servers
    avg_cores = sum(server["cpu_cores"] for server in servers_data) / len(servers_data)
    avg_memory = sum(server["memory_gb"] for server in servers_data) / len(servers_data)
    avg_nics = sum(server["nic_count"] for server in servers_data) / len(servers_data)
    avg_disk = sum(server["system_disk_gb"] for server in servers_data) / len(servers_data)
    
    # Normalize to percentage of recommendation
    actual_norm = [
        min(avg_cores / recommended[0] * 100, 150),  # Cap at 150% for visualization
        min(avg_memory / recommended[1] * 100, 150),
        min(avg_nics / recommended[2] * 100, 150),
        min(avg_disk / recommended[3] * 100, 150)
    ]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100],
        theta=categories,
        fill='toself',
        name='Recommended',
        fillcolor='rgba(255, 165, 0, 0.2)',
        line=dict(color='orange')
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=actual_norm,
        theta=categories,
        fill='toself',
        name='Your Configuration',
        fillcolor='rgba(0, 128, 255, 0.2)',
        line=dict(color='blue')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 150]
            )),
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig)
    
    # Show summary table of all servers
    st.subheader("Server Configuration Summary")
    
    # Prepare summary DataFrame
    server_summary = []
    for server in servers_data:
        server_summary.append({
            "Name": server["name"],
            "Role": server["role"],
            "CPU Cores": server["cpu_cores"],
            "Memory (GB)": server["memory_gb"],
            "NICs": server["nic_count"],
            "System Disk (GB)": server["system_disk_gb"]
        })
    
    summary_df = pd.DataFrame(server_summary)
    st.table(summary_df)
    
    # Hardware best practices
    st.header("Hardware Best Practices")
    
    best_practices = [
        "Use homogeneous hardware for all cluster nodes",
        "Ensure all hardware is on the Windows Server Catalog",
        "Provide sufficient resources for the expected VM workload",
        "Configure hardware-level redundancy (power supplies, network adapters)",
        "Server names should not exceed 15 characters",
        "Plan for future growth with additional capacity",
        "Use enterprise-grade hardware for production environments"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: Introduction", key="prev_intro"):
            st.session_state.current_step = 0
            st.rerun()
    
    with col2:
        st.button("Next: Software Requirements", on_click=confirm_hardware_configuration)
