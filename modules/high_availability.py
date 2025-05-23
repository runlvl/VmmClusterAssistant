import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.high_availability_validator import (
    validate_ha_configuration,
    validate_service_account,
    create_ha_visualization,
    estimate_ha_requirements
)

# Helper functions for high availability configuration

def _initialize_ha_config(deployment_type="hyperv"):
    """Initialize high availability configuration in session state if not present."""
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "ha" not in st.session_state.configuration:
        # Default values based on deployment type
        if deployment_type == "hyperv":
            st.session_state.configuration["ha"] = {
                "enabled": True,
                "cluster": {
                    "name": "HV-Cluster",
                    "node_count": 2,
                    "quorum_type": "NodeAndDiskMajority",
                    "witness_type": "DiskWitness"
                }
            }
        else:
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

def _save_ha_configuration(ha_enabled, cluster_name, cluster_ip, node_count, quorum_type, 
                         witness_type, witness_resource, vmm_service_account, library_ha, 
                         library_share, dkm_enabled, vmm_db_ha):
    """Save high availability configuration to session state."""
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
    
    # Move to next step - which depends on deployment type
    if st.session_state.configuration.get("deployment_type", "hyperv") == "hyperv":
        # For Hyper-V only, skip the SCVMM-specific steps
        st.session_state.current_step = 7  # Documentation generation step
    else:
        st.session_state.current_step = 7  # Backup & restore is next
    
    st.rerun()

def _render_ha_options(deployment_type):
    """Render high availability options UI component."""
    if deployment_type == "hyperv":
        ha_enabled = st.checkbox(
            "Enable High Availability for Hyper-V",
            value=True,
            help="Deploy Hyper-V in a highly available configuration"
        )
    else:
        ha_enabled = st.checkbox(
            "Enable High Availability for Hyper-V and SCVMM",
            value=True,
            help="Deploy both Hyper-V and SCVMM in a highly available configuration"
        )
    
    if not ha_enabled:
        st.warning("High availability is strongly recommended for production environments.")
    
    return ha_enabled

def _render_cluster_configuration(deployment_type, ha_enabled):
    """Render cluster configuration UI component."""
    if not ha_enabled:
        # Default values for non-HA deployment
        return "HYPERV-Cluster", "192.168.1.200", "NodeAndDiskMajority", "DiskWitness", "\\\\?\\Volume{GUID}\\"
    
    st.header("Failover Cluster Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Set default cluster name based on deployment type
        default_cluster_name = "HV-Cluster" if deployment_type == "hyperv" else "VMM-Cluster"
        
        cluster_name = st.text_input(
            "Cluster Name",
            value=default_cluster_name,
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
    
    # Configure quorum/witness settings
    col1, col2 = st.columns(2)
    
    with col1:
        quorum_witness_type = st.selectbox(
            "Quorum/Witness Type",
            options=["Node Majority", "Disk Witness", "File Share Witness", "Cloud Witness"],
            index=1,
            help="Select the quorum/witness type for the cluster"
        )
        
        # Map selection to internal values
        quorum_type_map = {
            "Node Majority": "NodeMajority",
            "Disk Witness": "NodeAndDiskMajority",
            "File Share Witness": "NodeAndFileShareMajority",
            "Cloud Witness": "NodeAndCloudWitness"
        }
        quorum_type = quorum_type_map[quorum_witness_type]
        
        # Information about quorum/witness types
        with st.expander("About Quorum/Witness Types"):
            st.markdown("""
            **Node Majority**: Suitable for clusters with an odd number of nodes.
            
            **Disk Witness**: Recommended for most clusters with shared storage. Uses a small shared disk as quorum witness.
            
            **File Share Witness**: For clusters without shared storage or odd node count. Uses a file share as witness.
            
            **Cloud Witness**: Modern approach using Azure storage account as witness. Ideal for geo-distributed clusters.
            """)
    
    with col2:
        # Show appropriate configuration fields based on witness type
        witness_type_map = {
            "NodeMajority": "None",
            "NodeAndDiskMajority": "DiskWitness",
            "NodeAndFileShareMajority": "FileShareWitness",
            "NodeAndCloudWitness": "CloudWitness"
        }
        witness_type = witness_type_map.get(quorum_type, "DiskWitness")
        
        # Show appropriate witness configuration based on the selected type
        if witness_type == "None":
            st.info("Node Majority quorum does not require a witness.")
            witness_resource = "None"
        elif witness_type == "DiskWitness":
            st.info("Configure disk witness for the cluster")
            witness_resource = st.text_input(
                "Witness Disk Path",
                value="Q:\\",
                help="Drive letter for the disk witness (small disk, 1GB minimum)"
            )
        elif witness_type == "FileShareWitness":
            st.info("Configure file share witness for the cluster")
            witness_resource = st.text_input(
                "Witness File Share Path",
                value="\\\\server\\share",
                help="UNC path to the file share witness"
            )
        else:  # CloudWitness
            st.info("Configure Azure cloud witness for the cluster")
            storage_account = st.text_input(
                "Azure Storage Account Name",
                value="",
                help="Name of the Azure storage account"
            )
            storage_key = st.text_input(
                "Azure Storage Key",
                type="password",
                help="Primary key for the Azure storage account"
            )
            witness_resource = storage_account
            # Store both in session state
            st.session_state.configuration["cloud_witness_account"] = storage_account
            st.session_state.configuration["cloud_witness_key"] = storage_key
    
    return cluster_name, cluster_ip, quorum_type, witness_type, witness_resource

def _render_scvmm_configuration(deployment_type, has_software_config):
    """Render SCVMM-specific HA configuration UI component."""
    if deployment_type != "scvmm":
        # Default values for non-SCVMM deployment
        return "", False, False, False, ""
    
    st.header("SCVMM Configuration")
    
    # Get existing service account value if available
    default_vmm_service_account = "DOMAIN\\svc_vmm"
    if has_software_config and "service_account" in st.session_state.configuration["software"]:
        default_vmm_service_account = st.session_state.configuration["software"]["service_account"]
    
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
    
    return vmm_service_account, dkm_enabled, vmm_db_ha, library_ha, library_share

def _display_validation_results(validation_results):
    """Display high availability validation results."""
    if not validation_results["status"]:
        st.error("High availability configuration has errors that must be corrected.")
        for error in validation_results["errors"]:
            st.error(error)
    
    for warning in validation_results["warnings"]:
        st.warning(warning)
    
    for recommendation in validation_results["recommendations"]:
        st.info(f"Recommendation: {recommendation}")

def _display_ha_visualization_and_requirements(ha_config, node_count):
    """Display high availability architecture visualization and requirements."""
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

def _display_ha_best_practices():
    """Display high availability best practices."""
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

def render_high_availability():
    """Render the high availability configuration page."""
    st.title("High Availability Configuration")
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    if deployment_type == "hyperv":
        st.write("Configure high availability settings for your Hyper-V cluster. Proper HA configuration is essential for maintaining service continuity.")
    else:
        st.write("Configure high availability settings for your Hyper-V cluster with SCVMM. Proper HA configuration is essential for maintaining service continuity.")
    
    # Initialize HA configuration in session state if not present
    _initialize_ha_config(deployment_type)
    
    # Get number of Hyper-V hosts from hardware configuration
    node_count = st.session_state.configuration.get("hardware", {}).get("host_count", 2)
    
    # Render high availability options
    ha_enabled = _render_ha_options(deployment_type)
    
    # Render cluster configuration (if HA is enabled)
    cluster_name, cluster_ip, quorum_type, witness_type, witness_resource = _render_cluster_configuration(
        deployment_type, ha_enabled
    )
    
    # Check if software configuration exists
    has_software_config = "software" in st.session_state.configuration
    
    # Render SCVMM-specific configuration (if applicable)
    if deployment_type == "scvmm" and ha_enabled:
        vmm_service_account, dkm_enabled, vmm_db_ha, library_ha, library_share = _render_scvmm_configuration(
            deployment_type, has_software_config
        )
        use_vmm = True
    else:
        # Default values for non-VMM deployment
        vmm_service_account = ""
        dkm_enabled = False
        vmm_db_ha = False
        library_ha = False
        library_share = ""
        use_vmm = False
    
    # HA validation section
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
    _display_validation_results(validation_results)
    
    # Display HA visualization and requirements (if HA is enabled)
    if ha_enabled:
        _display_ha_visualization_and_requirements(ha_config, node_count)
    
    # Display HA best practices
    _display_ha_best_practices()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    # Set previous button based on deployment type
    prev_step_text = "Previous: Storage Configuration" if deployment_type == "hyperv" else "Previous: Security Settings"
    prev_step_key = "prev_storage" if deployment_type == "hyperv" else "prev_security"
    prev_step_num = 5 if deployment_type == "hyperv" else 6
    
    with col1:
        if st.button(prev_step_text, key=prev_step_key):
            st.session_state.current_step = prev_step_num
            st.rerun()
    
    # Set next button based on deployment type
    next_step_text = "Next: Generate Documentation" if deployment_type == "hyperv" else "Next: Backup & Restore"
    next_step_key = "next_doc" if deployment_type == "hyperv" else "next_backup"
    
    with col2:
        next_button = st.button(next_step_text, key=next_step_key)
        if next_button:
            if ha_enabled and not validation_results["status"]:
                st.error("Please correct the high availability configuration errors before proceeding.")
            else:
                _save_ha_configuration(
                    ha_enabled, cluster_name, cluster_ip, node_count, quorum_type, 
                    witness_type, witness_resource, vmm_service_account, library_ha, 
                    library_share, dkm_enabled, vmm_db_ha
                )