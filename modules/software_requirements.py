import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.requirements import get_software_requirements
from utils.navigation import go_to_hardware, go_to_network

def render_software_requirements():
    """Render the software requirements page with separate tabs for Hyper-V hosts and SCVMM."""
    st.title("Software Requirements")
    
    # Get software requirements data
    sw_requirements = get_software_requirements()
    
    # Check deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    # Introduction text
    if deployment_type == "hyperv":
        st.write("Before implementing a Hyper-V cluster, ensure your software environment meets the following requirements.")
    else:
        st.write("Before implementing a Hyper-V cluster with SCVMM, ensure your software environment meets the following requirements.")
    
    # Create two tabs: one for Hyper-V host requirements, another for SCVMM requirements
    host_tab, scvmm_tab = st.tabs(["Hyper-V Host Requirements", "SCVMM Requirements (Optional)"])
    
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
        st.session_state.current_step = 4  # Move to network configuration (index 4 in the steps list)

    # OS version selection (used by both tabs)
    os_version_map = {
        "Windows Server 2025": "2025",
        "Windows Server 2022": "2022"
    }
    
    #########################
    # Tab 1: Hyper-V Hosts  #
    #########################
    with host_tab:
        # Operating System Requirements
        st.header("Operating System Requirements")
        
        os_version = st.selectbox(
            "Operating System Version",
            options=list(os_version_map.keys()),
            index=0,
            help="Select the operating system version to use for your Hyper-V cluster hosts"
        )
        
        # Show OS requirements
        os_req_df = pd.DataFrame(sw_requirements["os_requirements"])
        st.table(os_req_df)
        
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
        
        # File system requirements for hosts
        st.header("File System Requirements")
        
        fs_df = pd.DataFrame(sw_requirements["file_system_requirements"])
        st.table(fs_df)
        
        # Create feature visualization for hosts
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
        
        # Host-specific best practices
        st.header("Hyper-V Host Best Practices")
        
        host_best_practices = [
            "Keep all software components updated with the latest security patches",
            "Install only necessary roles and features",
            "Use consistent software versions across all servers",
            "Configure Windows Firewall with appropriate exceptions",
            "Enable performance counters for monitoring",
            "Use the same hardware configuration for all cluster nodes when possible"
        ]
        
        for practice in host_best_practices:
            st.markdown(f"- {practice}")
    
    ##########################
    # Tab 2: SCVMM (Optional)#
    ##########################
    with scvmm_tab:
        use_scvmm = st.checkbox("Use System Center Virtual Machine Manager (SCVMM)", 
                               value=(deployment_type == "scvmm"),
                               help="SCVMM provides centralized management but is completely optional")
        
        if use_scvmm:
            # System Center and SQL Server Requirements section
            st.header("System Center and SQL Server Requirements")
            
            col1, col2 = st.columns(2)
            
            with col1:
                vmm_version = st.selectbox(
                    "SCVMM Version",
                    options=["System Center 2025", "System Center 2022"],
                    index=0,
                    help="Select the System Center VMM version"
                )
            
            with col2:
                sql_version = st.selectbox(
                    "SQL Server Version",
                    options=["SQL Server 2022", "SQL Server 2022 Express"],
                    index=0,
                    help="Select the SQL Server version for the VMM database"
                )
            
            # VMM Requirements table
            vmm_req_df = pd.DataFrame(sw_requirements["vmm_requirements"])
            st.subheader("SCVMM Version Requirements")
            st.table(vmm_req_df)
            
            # SQL Requirements table
            sql_req_df = pd.DataFrame(sw_requirements["sql_requirements"])
            st.subheader("SQL Server Requirements")
            st.table(sql_req_df)
            
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
            
            # Additional software for SCVMM
            st.header("Additional SCVMM Requirements")
            
            col1, col2 = st.columns(2)
            
            with col1:
                adk_version = st.selectbox(
                    "Windows ADK Version",
                    options=["Windows 11 ADK", "Windows 10 ADK"],
                    index=0,
                    help="Select the Windows Assessment and Deployment Kit (ADK) version"
                )
            
            # Service accounts configuration
            st.header("SCVMM Service Accounts and Container Configuration")
            
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
            
            # Software compatibility matrix for SCVMM
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
                    "Compatible" if "2022" in vmm_version and "2022" in os_version or "2025" in vmm_version and "2025" in os_version else "Check Compatibility",
                    "Compatible" if "2022" in sql_version and "2022" in os_version or "2019" in sql_version and "2022" in os_version else "Check Compatibility",
                    "Compatible" if "2022" in sql_version and "2022" in vmm_version or "2019" in sql_version and "2022" in vmm_version else "Check Compatibility",
                    "Compatible" if "11" in adk_version and "2022" in os_version or "10" in adk_version and "2022" in os_version else "Check Compatibility"
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
            
            # Use the newer Styler.map method instead of the deprecated applymap
            styled_df = compat_df.style.map(highlight_compatibility, subset=['Status'])
            st.table(styled_df)
            
            # SCVMM-specific best practices
            st.header("SCVMM Best Practices")
            
            scvmm_best_practices = [
                "Do not install VMM on the Hyper-V host partition",
                "Use dedicated service accounts with least privilege",
                "Back up the DKM container configuration in Active Directory",
                "Ensure SQL Server has sufficient resources",
                "Use distributed installation for large environments",
                "Regularly back up the VMM database"
            ]
            
            for practice in scvmm_best_practices:
                st.markdown(f"- {practice}")
        else:
            # Default values for when not using SCVMM
            vmm_version = "None"
            sql_version = "None"
            sql_server = ""
            sql_instance = ""
            adk_version = "None"
            service_account = ""
            dkm_container = ""
            vmm_server_name = ""
            
            st.info("System Center Virtual Machine Manager (SCVMM) is optional and not selected. Your Hyper-V cluster will operate without centralized management.")
            
            # Show some basic advantages of SCVMM
            st.header("SCVMM Benefits (Not Selected)")
            st.markdown("""
            While SCVMM is completely optional, it provides these benefits:
            - Centralized management of multiple Hyper-V clusters
            - Simplified VM template management
            - Network virtualization capabilities
            - Advanced library management
            - Comprehensive reporting and monitoring
            
            You can always add SCVMM later if needed.
            """)
    
    # Navigation buttons (outside of tabs, visible in both)
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Direct navigation to Hardware Requirements
        prev_button = st.button("← Hardware Requirements", use_container_width=True)
        if prev_button:
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        # Call confirm function and direct navigation to Network Configuration
        next_button = st.button("Network Configuration →", use_container_width=True)
        if next_button:
            confirm_software_configuration()
            st.session_state.current_step = 4
            st.rerun()
