import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.high_availability_validator import (
    validate_ha_configuration,
    validate_service_account,
    create_ha_visualization,
    estimate_ha_requirements
)

def render_high_availability():
    """Render the high availability configuration page."""
    st.title("High Availability Configuration")
    
    st.write("Configure high availability settings for your VMM cluster. Proper HA configuration is essential for maintaining service continuity.")
    
    # Initialize HA configuration in session state if not present
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "ha" not in st.session_state.configuration:
        st.session_state.configuration["ha"] = {
            "enabled": True,
            "cluster": {
                "name": "VMM-Cluster",
                "node_count": 2,
                "quorum_type": "NodeAndDiskMajority",
                "witness_type": "DiskWitness"
            },
            "vmm_service_account": "DOMAIN\\svc_vmm",
            "library_ha": True
        }
    
    # Function to update session state when HA configuration is confirmed
    def confirm_ha_configuration():
        st.session_state.configuration["ha"] = {
            "enabled": ha_enabled,
            "cluster": {
                "name": cluster_name,
                "ip": cluster_ip,
                "node_count": node_count,
                "quorum_type": quorum_type,
                "witness_type": witness_type,
                "witness_resource": witness_resource
            },
            "vmm_service_account": vmm_service_account,
            "library_ha": library_ha,
            "library_share": library_share,
            "dkm_enabled": dkm_enabled,
            "vmm_db_ha": vmm_db_ha
        }
        
        if "completed_steps" not in st.session_state:
            st.session_state.completed_steps = set()
        
        st.session_state.completed_steps.add(6)  # Mark HA step as completed
        st.session_state.current_step = 7  # Move to next step (backup & restore)
        st.rerun()
    
    # High Availability Options
    st.header("High Availability Options")
    
    ha_enabled = st.checkbox(
        "Enable High Availability for VMM",
        value=True,
        help="Deploy VMM in a highly available configuration"
    )
    
    if not ha_enabled:
        st.warning("High availability is strongly recommended for production environments.")
    
    # Get existing values from software configuration
    default_vmm_service_account = "DOMAIN\\svc_vmm"
    if "software" in st.session_state.configuration and "service_account" in st.session_state.configuration["software"]:
        default_vmm_service_account = st.session_state.configuration["software"]["service_account"]
    
    # Get number of Hyper-V hosts from hardware configuration
    node_count = st.session_state.configuration.get("hardware", {}).get("host_count", 2)
    
    # Cluster Configuration
    if ha_enabled:
        st.header("Failover Cluster Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cluster_name = st.text_input(
                "Cluster Name",
                value="VMM-Cluster",
                help="Enter the name for the failover cluster"
            )
            
            if len(cluster_name) > 15:
                st.error("Cluster name exceeds 15 characters. Please shorten the name.")
        
        with col2:
            cluster_ip = st.text_input(
                "Cluster IP Address",
                value="192.168.1.200",
                help="Enter the IP address for the cluster"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            quorum_type = st.selectbox(
                "Quorum Type",
                options=["NodeMajority", "NodeAndDiskMajority", "NodeAndFileShareMajority", "NodeAndCloudWitness"],
                index=1,
                help="Select the quorum type for the cluster"
            )
            
            # Information about quorum types
            with st.expander("About Quorum Types"):
                st.markdown("""
                **NodeMajority**: Suitable for clusters with an odd number of nodes.
                
                **NodeAndDiskMajority**: Recommended for most clusters with shared storage.
                
                **NodeAndFileShareMajority**: For clusters without shared storage or odd node count.
                
                **NodeAndCloudWitness**: Modern approach using Azure storage account as witness.
                """)
        
        with col2:
            # The witness type is determined by the quorum type
            if quorum_type == "NodeMajority":
                witness_type = "None"
                st.info("Node Majority quorum does not require a witness.")
            elif quorum_type == "NodeAndDiskMajority":
                witness_type = "DiskWitness"
                st.info("Disk Witness will be used (required for Node And Disk Majority).")
            elif quorum_type == "NodeAndFileShareMajority":
                witness_type = "FileShareWitness"
                st.info("File Share Witness will be used (required for Node And File Share Majority).")
            elif quorum_type == "NodeAndCloudWitness":
                witness_type = "CloudWitness"
                st.info("Cloud Witness will be used (required for Node And Cloud Witness).")
            else:
                witness_type = "DiskWitness"
        
        # Witness resource based on type
        if witness_type == "DiskWitness":
            witness_resource = st.text_input(
                "Witness Disk Path",
                value="\\\\?\\Volume{GUID}\\",
                help="Enter the path to the quorum disk"
            )
        elif witness_type == "FileShareWitness":
            witness_resource = st.text_input(
                "Witness File Share Path",
                value="\\\\server\\share",
                help="Enter the UNC path to the file share witness"
            )
        else:  # CloudWitness
            witness_resource = st.text_input(
                "Azure Storage Account Name",
                value="",
                help="Enter the Azure storage account name for Cloud Witness"
            )
        
        # Optional VMM High Availability Configuration
        st.header("SCVMM (Optional)")
        
        use_vmm = st.checkbox(
            "Deploy with System Center VMM",
            value=False,
            help="Include System Center Virtual Machine Manager in the deployment"
        )
        
        if use_vmm:
            vmm_service_account = st.text_input(
                "VMM Service Account",
                value=default_vmm_service_account,
                help="Enter the service account for VMM (format: DOMAIN\\username)"
            )
            
            validate_result = validate_service_account(vmm_service_account)
            if not validate_result["status"]:
                for error in validate_result["errors"]:
                    st.error(error)
            for warning in validate_result["warnings"]:
                st.warning(warning)
            
            dkm_enabled = st.checkbox(
                "Enable Distributed Key Management (DKM)",
                value=True,
                help="Store encryption keys securely in Active Directory (required for HA)"
            )
            
            if not dkm_enabled:
                st.error("Distributed Key Management is required for high availability VMM deployments.")
            
            vmm_db_ha = st.checkbox(
                "Configure SQL Server for High Availability",
                value=True,
                help="Deploy SQL Server in a highly available configuration"
            )
            
            # VMM Library High Availability
            st.header("VMM Library")
            
            library_ha = st.checkbox(
                "Configure Highly Available VMM Library",
                value=True,
                help="Deploy VMM library on a highly available file share"
            )
            
            if library_ha:
                library_share = st.text_input(
                    "Library Share Path",
                    value="\\\\fileserver\\VMMLibrary",
                    help="Enter the UNC path to the library share"
                )
            else:
                library_share = ""
                st.warning("A highly available VMM library is recommended for production environments.")
        else:
            # Default values for non-VMM deployment
            vmm_service_account = ""
            dkm_enabled = False
            vmm_db_ha = False
            library_ha = False
            library_share = ""
    else:
        # Default values for non-HA deployment
        cluster_name = "HYPERV-Cluster"
        cluster_ip = "192.168.1.200"
        quorum_type = "NodeAndDiskMajority"
        witness_type = "DiskWitness"
        witness_resource = "\\\\?\\Volume{GUID}\\"
        use_vmm = False
        vmm_service_account = ""
        dkm_enabled = False
        vmm_db_ha = False
        library_ha = False
        library_share = ""
    
    # HA validation
    st.header("High Availability Validation")
    
    # Compile configuration for validation
    ha_config = {
        "enabled": ha_enabled,
        "cluster": {
            "name": cluster_name,
            "node_count": node_count,
            "quorum_type": quorum_type,
            "witness_type": witness_type,
            "witness_resource": witness_resource if ha_enabled else ""
        },
        "use_vmm": use_vmm,
        "vmm_service_account": vmm_service_account if use_vmm else "",
        "library_ha": library_ha if use_vmm else False,
        "dkm_enabled": dkm_enabled if use_vmm else False,
        "vmm_db_ha": vmm_db_ha if use_vmm else False
    }
    
    # Validate HA configuration
    validation_results = validate_ha_configuration(ha_config)
    
    # Display validation results
    if not validation_results["status"]:
        st.error("High availability configuration has errors that must be corrected.")
        for error in validation_results["errors"]:
            st.error(error)
    
    for warning in validation_results["warnings"]:
        st.warning(warning)
    
    for recommendation in validation_results["recommendations"]:
        st.info(f"Recommendation: {recommendation}")
    
    if ha_enabled:
        # HA visualization
        st.subheader("High Availability Architecture Visualization")
        
        # Create HA visualization
        fig = create_ha_visualization(ha_config)
        st.plotly_chart(fig)
        
        # Estimate HA requirements
        st.subheader("High Availability Requirements")
        
        ha_requirements = estimate_ha_requirements(node_count)
        
        # Display requirements
        with st.expander("Server Requirements", expanded=False):
            server_df = pd.DataFrame([
                {
                    "Server": server["name"],
                    "CPU Cores": server["cpu_cores"],
                    "Memory (GB)": server["memory_gb"],
                    "OS Disk (GB)": server["os_disk_gb"],
                    "Network Adapters": server["network_adapters"]
                }
                for server in ha_requirements["servers"]
            ])
            
            st.table(server_df)
        
        with st.expander("Storage Requirements", expanded=False):
            st.write(f"**Quorum Disk:** {ha_requirements['storage']['quorum_disk_gb']} GB")
            st.write(f"**Witness Type:** {ha_requirements['storage']['witness_type']}")
            
            csv_df = pd.DataFrame([
                {
                    "Volume": volume["name"],
                    "Size (GB)": volume["size_gb"],
                    "Purpose": volume["purpose"]
                }
                for volume in ha_requirements["storage"]["csv_volumes"]
            ])
            
            st.table(csv_df)
        
        with st.expander("Network Requirements", expanded=False):
            for network_type, network_config in ha_requirements["network"].items():
                if isinstance(network_config, dict):
                    st.write(f"**{network_type.replace('_', ' ').title()}:** {network_config.get('bandwidth', 'N/A')}, Redundant: {network_config.get('redundant', False)}")
            
            st.write("**Dedicated Networks:** " + ("Yes" if ha_requirements["network"]["dedicated_networks"] else "No"))
        
        # HA recommendations
        st.write("**High Availability Recommendations:**")
        for recommendation in ha_requirements["recommendations"]:
            st.markdown(f"- {recommendation}")
    
    # High Availability best practices
    st.header("High Availability Best Practices")
    
    best_practices = [
        "Test planned and unplanned failover scenarios regularly",
        "Ensure the cluster validation test passes before implementing",
        "Configure proper quorum settings to prevent split-brain scenarios",
        "Document failover procedures for administrators",
        "Implement monitoring for cluster health",
        "Use identical hardware for all cluster nodes",
        "Configure at least two separate networks for cluster communication",
        "Ensure the VMM database is also highly available",
        "Configure the VMM library on a highly available file share",
        "Test the recovery of a failed node before going to production"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: Security Settings", key="prev_security"):
            st.session_state.current_step = 5
            st.rerun()
    
    with col2:
        next_button = st.button("Next: Backup & Restore", key="next_backup")
        if next_button:
            if ha_enabled and not validation_results["status"]:
                st.error("Please correct the high availability configuration errors before proceeding.")
            else:
                confirm_ha_configuration()
