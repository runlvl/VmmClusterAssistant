import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.requirements import get_software_requirements

def render_software_requirements():
    """Render the software requirements page."""
    st.title("Software Requirements")
    
    # Get software requirements data
    sw_requirements = get_software_requirements()
    
    st.write("Before implementing a VMM cluster, ensure your software environment meets the following requirements.")
    
    # Function to update session state when requirements are confirmed
    def confirm_software_configuration():
        if "configuration" not in st.session_state:
            st.session_state.configuration = {}
        if "software" not in st.session_state.configuration:
            st.session_state.configuration["software"] = {}
        
        st.session_state.configuration["software"] = {
            "os": os_version,
            "os_version": os_version_map.get(os_version, ""),
            "vmm_version": vmm_version,
            "sql_version": sql_version,
            "adk_version": adk_version,
            "service_account": service_account,
            "dkm_container": dkm_container,
            "vmm_server_name": vmm_server_name,
            "sql_server": sql_server,
            "sql_instance": sql_instance,
            "features": {
                "failover_clustering": failover_clustering,
                "hyper_v": hyper_v,
                "mpio": mpio,
                "data_deduplication": data_deduplication
            }
        }
        
        if "completed_steps" not in st.session_state:
            st.session_state.completed_steps = set()
        
        st.session_state.completed_steps.add(2)  # Mark software step as completed
        st.session_state.current_step = 3  # Move to next step (network configuration)
        st.rerun()

    # Operating System Requirements
    st.header("Operating System Requirements")
    
    # OS version selection
    os_version_map = {
        "Windows Server 2022": "2022",
        "Windows Server 2019": "2019",
        "Windows Server 2016": "2016"
    }
    
    os_version = st.selectbox(
        "Operating System Version",
        options=list(os_version_map.keys()),
        index=0,
        help="Select the operating system version to use for your VMM cluster"
    )
    
    # Show OS requirements
    os_req_df = pd.DataFrame(sw_requirements["os_requirements"])
    st.table(os_req_df)
    
    # VMM and SQL Version
    st.header("System Center and SQL Server Requirements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vmm_version = st.selectbox(
            "VMM Version",
            options=["System Center 2022", "System Center 2019", "System Center 2016"],
            index=0,
            help="Select the System Center VMM version"
        )
    
    with col2:
        sql_version = st.selectbox(
            "SQL Server Version",
            options=["SQL Server 2022", "SQL Server 2019", "SQL Server 2017", "SQL Server 2016"],
            index=0,
            help="Select the SQL Server version for the VMM database"
        )
    
    # SQL Server settings
    st.subheader("SQL Server Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sql_server = st.text_input(
            "SQL Server Name",
            value="SQLSERVER",
            help="Enter the SQL Server name"
        )
    
    with col2:
        sql_instance = st.text_input(
            "SQL Instance",
            value="MSSQLSERVER",
            help="Enter the SQL instance name (MSSQLSERVER for default instance)"
        )
    
    # Additional software
    st.header("Additional Required Software")
    
    col1, col2 = st.columns(2)
    
    with col1:
        adk_version = st.selectbox(
            "Windows ADK Version",
            options=["Windows 11 ADK", "Windows 10 ADK"],
            index=0,
            help="Select the Windows Assessment and Deployment Kit (ADK) version"
        )
    
    # Required Windows Features
    st.header("Required Windows Features")
    
    # Show requirements and allow selection
    features_df = pd.DataFrame(sw_requirements["required_features"])
    
    # Display features table
    st.table(features_df)
    
    # Checkboxes for features
    col1, col2 = st.columns(2)
    
    with col1:
        hyper_v = st.checkbox("Hyper-V", value=True, help="Required for virtualization")
        failover_clustering = st.checkbox("Failover Clustering", value=True, help="Required for high availability")
    
    with col2:
        mpio = st.checkbox("Multipath I/O", value=True, help="Required for redundant storage connectivity")
        data_deduplication = st.checkbox("Data Deduplication", value=False, help="Optional for storage efficiency")
    
    # Account configuration
    st.header("Service Accounts and Container Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service_account = st.text_input(
            "VMM Service Account",
            value="DOMAIN\\svc_vmm",
            help="Enter the service account for VMM (format: DOMAIN\\username)"
        )
        
        if "\\" not in service_account and "@" not in service_account:
            st.warning("Service account should be in domain\\username or username@domain format")
    
    with col2:
        dkm_container = st.text_input(
            "DKM Container Name",
            value="VMM_DKM",
            help="Enter the name for the Distributed Key Management container in Active Directory"
        )
    
    # VMM Server Name
    st.subheader("VMM Server Configuration")
    vmm_server_name = st.text_input(
        "VMM Server Name",
        value="VMMSERVER",
        help="Enter the name for the VMM server (for cluster configuration)"
    )
    
    if len(vmm_server_name) > 15:
        st.error("VMM server name exceeds 15 characters. Please shorten the name.")
    
    # Software validation visualization
    st.header("Software Compatibility Matrix")
    
    # Create compatibility matrix
    compatibility = {
        "Component Pair": [
            "OS + VMM",
            "OS + SQL",
            "VMM + SQL",
            "OS + ADK"
        ],
        "Status": [
            "Compatible" if "2022" in vmm_version and "2022" in os_version or "2019" in vmm_version and "2019" in os_version else "Check Compatibility",
            "Compatible" if "2022" in sql_version and "2022" in os_version or "2019" in sql_version and "2019" in os_version else "Check Compatibility",
            "Compatible" if "2022" in sql_version and "2022" in vmm_version or "2019" in sql_version and "2019" in vmm_version else "Check Compatibility",
            "Compatible" if "11" in adk_version and "2022" in os_version or "10" in adk_version and "2019" in os_version else "Check Compatibility"
        ]
    }
    
    compat_df = pd.DataFrame(compatibility)
    
    # Apply conditional formatting
    def highlight_compatibility(val):
        if val == "Compatible":
            return 'background-color: #CCFFCC'
        elif val == "Check Compatibility":
            return 'background-color: #FFFFCC'
        else:
            return 'background-color: #FFCCCC'
    
    styled_df = compat_df.style.applymap(highlight_compatibility, subset=['Status'])
    st.table(styled_df)
    
    # Create feature visualization
    features = ["Hyper-V", "Failover Clustering", "Multipath I/O", "Data Deduplication"]
    feature_values = [hyper_v, failover_clustering, mpio, data_deduplication]
    feature_colors = ['green' if val else 'red' for val in feature_values]
    
    fig = go.Figure(data=[
        go.Bar(
            x=features,
            y=[1, 1, 1, 1],
            marker_color=feature_colors,
            text=["Enabled" if val else "Disabled" for val in feature_values],
            textposition="auto"
        )
    ])
    
    fig.update_layout(
        title="Windows Features Status",
        yaxis_visible=False,
        height=300
    )
    
    st.plotly_chart(fig)
    
    # Software best practices
    st.header("Software Best Practices")
    
    best_practices = [
        "Keep all software components updated with the latest security patches",
        "Install only necessary roles and features",
        "Do not install VMM on the Hyper-V host partition",
        "Use consistent software versions across all servers",
        "Configure Windows Firewall with appropriate exceptions",
        "Use dedicated service accounts with least privilege",
        "Back up the DKM container configuration in Active Directory"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: Hardware Requirements", key="prev_hardware"):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        st.button("Next: Network Configuration", on_click=confirm_software_configuration)
