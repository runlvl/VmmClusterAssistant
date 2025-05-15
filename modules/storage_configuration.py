import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.storage_validator import (
    validate_storage_configuration,
    create_storage_visualization,
    estimate_storage_needs
)

def _get_intro_text(deployment_type):
    """Get introduction text based on deployment type."""
    if deployment_type == "hyperv":
        return "Configure the storage settings for your Hyper-V cluster. Proper storage setup is essential for cluster shared volumes, VM storage, and high availability."
    else:
        return "Configure the storage settings for your Hyper-V cluster with SCVMM. Proper storage setup is essential for cluster shared volumes, VM storage, SCVMM library, and high availability."

def _save_storage_configuration(storage_type, csv_volumes, csv_count, quorum_disk, mpio_enabled, 
                          shared_between_clusters, redundancy, storage_connectivity, filesystem, is_s2d, hyper_v_hosts):
    """Save storage configuration to session state."""
    st.session_state.configuration["storage"] = {
        "storage_type": storage_type,
        "csv_volumes": csv_volumes,
        "csv_count": int(csv_count),
        "quorum_disk": quorum_disk,
        "mpio_enabled": mpio_enabled,
        "shared_between_clusters": shared_between_clusters,
        "redundancy": redundancy,
        "storage_connectivity": storage_connectivity,
        "filesystem": filesystem, 
        "is_s2d": is_s2d,
        "host_count": hyper_v_hosts
    }
    
    if "completed_steps" not in st.session_state:
        st.session_state.completed_steps = set()
    
    st.session_state.completed_steps.add(4)  # Mark storage configuration step as completed
    st.session_state.current_step = 5  # Move to next step (security settings)
    st.rerun()

def _initialize_storage_config():
    """Initialize storage configuration in session state if not present."""
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "storage" not in st.session_state.configuration:
        st.session_state.configuration["storage"] = {
            "storage_type": "SAN",
            "csv_volumes": [{"size_gb": 1000, "purpose": "VM Storage"}],
            "quorum_disk": {"size_gb": 1},
            "mpio_enabled": True
        }

def _render_storage_type_selection(hyper_v_hosts):
    """Render storage type selection section."""
    # Storage type selection
    storage_options = ["SAN", "iSCSI", "FC", "SMB", "Storage Spaces Direct (S2D)", "Local", "NVMe"]
    storage_type = st.selectbox(
        "Storage Type",
        options=storage_options,
        index=0,
        help="Select the type of storage for your cluster"
    )
    
    # Warning messages for specific storage types
    if storage_type == "Local":
        st.warning("⚠️ Local storage is not recommended for production clusters. Consider using shared storage.")
    
    if storage_type == "Storage Spaces Direct (S2D)":
        st.success("✅ Storage Spaces Direct (S2D) is a good choice for hyper-converged infrastructure.")
        
    is_s2d = storage_type == "Storage Spaces Direct (S2D)"
    
    # Storage connectivity
    if storage_type != "Local" and storage_type != "SMB":
        storage_connectivity = st.selectbox(
            "Storage Connectivity",
            options=["1 Gbps", "10 Gbps", "16 Gbps", "32 Gbps"],
            index=1,
            help="Select the connectivity speed for your storage"
        )
    else:
        storage_connectivity = "N/A"
    
    return storage_type, storage_connectivity, is_s2d

def _render_redundancy_options(is_s2d):
    """Render redundancy and filesystem options based on storage type."""
    col1, col2 = st.columns(2)
    
    with col1:
        # Change redundancy options based on storage type
        if is_s2d:
            redundancy_options = ["2-way mirror", "3-way mirror", "Parity"]
            redundancy_index = 0
            redundancy_help = "Select the redundancy level for your S2D storage"
        else:
            redundancy_options = ["RAID 1", "RAID 5", "RAID 6", "RAID 10", "None"]
            redundancy_index = 0
            redundancy_help = "Select the redundancy level for your storage"
            
        redundancy = st.selectbox(
            "Storage Redundancy",
            options=redundancy_options,
            index=redundancy_index,
            help=redundancy_help
        )
    
    with col2:
        # Show appropriate options based on storage type
        if not is_s2d:
            mpio_enabled = st.checkbox(
                "Enable MPIO (Multipath I/O)",
                value=True,
                help="Recommended: Enable MPIO for redundant storage connectivity"
            )
        else:
            mpio_enabled = True  # S2D always has built-in redundancy
            st.info("S2D includes built-in storage redundancy")
    
    return redundancy, mpio_enabled

def _render_filesystem_options(is_s2d, hyper_v_hosts):
    """Render filesystem options and CSV count selection."""
    col1, col2 = st.columns(2)
    
    with col1:
        if is_s2d:
            # For S2D, always use ReFS
            filesystem = "ReFS"
            st.info("ReFS is the recommended filesystem for Storage Spaces Direct")
        else:
            # For other storage types, NTFS is recommended
            filesystem_options = ["NTFS", "ReFS"]
            filesystem = st.selectbox(
                "Filesystem",
                options=filesystem_options,
                index=0,
                help="NTFS is recommended for traditional storage; ReFS is recommended for S2D"
            )
    
    with col2:
        # Ensure at least 1 CSV per host
        min_csv_count = hyper_v_hosts
        csv_count = st.number_input(
            "Number of CSV Volumes",
            min_value=min_csv_count,
            value=min_csv_count,
            help="Enter the number of Cluster Shared Volumes (CSVs) to create"
        )
        
        if csv_count < hyper_v_hosts:
            st.error(f"⚠️ You need at least {hyper_v_hosts} CSV volumes (1 per host)")
        else:
            st.success(f"✅ Good! You have at least one CSV per host ({csv_count} CSVs for {hyper_v_hosts} hosts)")
            
    return filesystem, csv_count

def _render_storage_estimator():
    """
    Render storage estimator UI component and return recommendations.
    
    Returns:
        dict: Storage recommendations including quorum disk and CSV volumes
    """
    col1, col2 = st.columns(2)
    
    with col1:
        vm_count = st.number_input(
            "Expected number of VMs",
            min_value=1,
            value=20,
            help="Enter the total number of VMs you plan to host"
        )
    
    with col2:
        avg_vm_size = st.number_input(
            "Average VM size (GB)",
            min_value=10,
            value=100,
            help="Enter the average disk size for each VM in GB"
        )
    
    # Calculate storage recommendations
    storage_recommendations = estimate_storage_needs(vm_count, avg_vm_size)
    
    st.subheader("Storage Recommendations")
    
    for recommendation in storage_recommendations["text"]:
        st.info(recommendation)
    
    st.subheader("Recommended Configuration")
    
    # Display quorum recommendation
    st.write(f"**Quorum Disk:** {storage_recommendations['quorum_disk']['size_gb']} GB")
    
    # Display CSV volume recommendations
    st.write("**CSV Volumes:**")
    csv_rec_df = pd.DataFrame([
        {
            "Volume": f"CSV {i+1}",
            "Size (GB)": volume["size_gb"],
            "Purpose": volume["purpose"]
        }
        for i, volume in enumerate(storage_recommendations["csv_volumes"])
    ])
    
    st.table(csv_rec_df)
    
    return storage_recommendations

def _render_quorum_disk_config():
    """
    Render quorum disk configuration UI component.
    
    Returns:
        dict: Quorum disk configuration
    """
    col1, col2 = st.columns(2)
    
    with col1:
        quorum_disk_size = st.number_input(
            "Quorum Disk Size (GB)",
            min_value=1,
            max_value=10,
            value=1,
            help="Recommended size: 1 GB"
        )
    
    with col2:
        quorum_disk_format = st.selectbox(
            "Quorum Disk Format",
            options=["NTFS"],
            index=0
        )
    
    # Create quorum disk configuration
    quorum_disk = {
        "size_gb": quorum_disk_size,
        "format": quorum_disk_format,
        "purpose": "Cluster quorum"
    }
    
    return quorum_disk

def _render_csv_configurations(csv_count, filesystem, redundancy, purpose_options=None):
    """
    Render CSV volume configurations based on the number specified.
    
    Args:
        csv_count: Number of CSV volumes to configure
        filesystem: Selected filesystem to use (NTFS or ReFS)
        redundancy: Default redundancy setting
        purpose_options: List of default purpose options for volumes
        
    Returns:
        list: List of configured CSV volumes
    """
    if purpose_options is None:
        purpose_options = ["VM Storage", "VM Templates", "ISO Library", "Backup Target", "General Storage"]
    
    # Create CSV volumes based on the number specified
    csv_volumes = []
    
    # Generate dynamic CSV volume configurations based on csv_count
    for i in range(int(csv_count)):
        with st.expander(f"CSV Volume {i+1}", expanded=(i == 0)):  # Only expand first volume by default
            col1, col2 = st.columns(2)
            
            with col1:
                csv_size = st.number_input(
                    "Volume Size (GB)",
                    min_value=100,
                    value=1000,
                    help="Enter the size of the CSV volume in GB",
                    key=f"csv_size_{i}"
                )
            
            with col2:
                # Set different default purposes for volumes if available in the options list
                default_purpose = purpose_options[i] if i < len(purpose_options) else f"VM Storage {i+1}"
                    
                csv_purpose = st.text_input(
                    "Purpose",
                    value=default_purpose,
                    help="Enter the purpose of this volume",
                    key=f"csv_purpose_{i}"
                )
            
            # Volume specific settings
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"Filesystem: {filesystem}")
            
            # Determine appropriate redundancy options based on storage type
            with col2:
                is_s2d = "mirror" in redundancy or "Parity" in redundancy
                if is_s2d:
                    redundancy_options = ["Same as Storage", "2-way mirror", "3-way mirror", "Parity"]
                else:
                    redundancy_options = ["Same as Storage", "RAID 1", "RAID 5", "RAID 6", "RAID 10", "None"]
                
                csv_redundancy = st.selectbox(
                    "Volume Redundancy",
                    options=redundancy_options,
                    index=0,
                    key=f"csv_redundancy_{i}"
                )
            
            # Add to CSV volumes with the pre-selected filesystem
            csv_volumes.append({
                "size_gb": csv_size,
                "purpose": csv_purpose,
                "format": filesystem,
                "redundancy": csv_redundancy if csv_redundancy != "Same as Storage" else redundancy
            })
    
    return csv_volumes

def _render_storage_summary(quorum_disk, csv_volumes):
    """
    Render storage configuration summary UI component.
    
    Args:
        quorum_disk: Quorum disk configuration
        csv_volumes: List of CSV volume configurations
        
    Returns:
        list: List of storage summary items
    """
    st.header("Storage Configuration Summary")
    
    # Show summary table of all volumes
    storage_summary = []
    
    # Add quorum disk
    storage_summary.append({
        "Volume": "Quorum Disk",
        "Size (GB)": quorum_disk["size_gb"],
        "Purpose": quorum_disk["purpose"],
        "Format": quorum_disk["format"]
    })
    
    # Add CSV volumes
    for i, volume in enumerate(csv_volumes):
        storage_summary.append({
            "Volume": f"CSV {i+1}",
            "Size (GB)": volume["size_gb"],
            "Purpose": volume["purpose"],
            "Format": volume["format"]
        })
    
    summary_df = pd.DataFrame(storage_summary)
    st.table(summary_df)
    
    # Calculate total storage
    total_size = quorum_disk["size_gb"] + sum(volume["size_gb"] for volume in csv_volumes)
    st.info(f"Total storage required: {total_size} GB ({total_size/1024:.2f} TB)")
    
    return storage_summary

def _validate_storage_config(storage_type, csv_volumes, quorum_disk, mpio_enabled, 
                           shared_between_clusters, redundancy, host_count):
    """
    Validate storage configuration and display results.
    
    Args:
        storage_type: Type of storage
        csv_volumes: List of CSV volume configurations
        quorum_disk: Quorum disk configuration
        mpio_enabled: Whether MPIO is enabled
        shared_between_clusters: Whether storage is shared between clusters
        redundancy: Storage redundancy setting
        host_count: Number of hosts
        
    Returns:
        dict: Validation results
    """
    st.header("Storage Configuration Validation")
    
    # Compile configuration for validation
    storage_config = {
        "storage_type": storage_type,
        "csv_volumes": csv_volumes,
        "quorum_disk": quorum_disk,
        "mpio_enabled": mpio_enabled,
        "shared_between_clusters": shared_between_clusters,
        "redundancy": redundancy,
        "host_count": host_count
    }
    
    # Validate storage configuration
    validation_results = validate_storage_configuration(storage_config)
    
    # Display validation results
    if not validation_results["status"]:
        st.error("Storage configuration has errors that must be corrected.")
        for error in validation_results["errors"]:
            st.error(error)
    
    for warning in validation_results["warnings"]:
        st.warning(warning)
    
    for recommendation in validation_results["recommendations"]:
        st.info(f"Recommendation: {recommendation}")
        
    return validation_results

def _render_storage_visualization(storage_type, csv_volumes, quorum_disk, mpio_enabled,
                                shared_between_clusters, redundancy, host_count):
    """
    Render storage architecture visualization.
    
    Args:
        storage_type: Type of storage
        csv_volumes: List of CSV volume configurations
        quorum_disk: Quorum disk configuration
        mpio_enabled: Whether MPIO is enabled
        shared_between_clusters: Whether storage is shared between clusters
        redundancy: Storage redundancy setting
        host_count: Number of hosts
    """
    st.subheader("Storage Architecture Visualization")
    
    # Create storage configuration for visualization
    storage_config = {
        "storage_type": storage_type,
        "csv_volumes": csv_volumes,
        "quorum_disk": quorum_disk,
        "mpio_enabled": mpio_enabled,
        "shared_between_clusters": shared_between_clusters,
        "redundancy": redundancy,
        "host_count": host_count
    }
    
    # Create storage visualization
    fig = create_storage_visualization(storage_config)
    st.plotly_chart(fig)

def _render_storage_best_practices():
    """Render storage best practices UI component."""
    st.header("Storage Best Practices")
    
    best_practices = [
        "Use shared storage for all cluster nodes",
        "Implement MPIO for redundant storage connectivity",
        "Use small (1-5 GB) LUN for quorum disk",
        "Do not share storage between different clusters",
        "Consider using multiple CSV volumes for better performance and management",
        "Place only highly available VMs on cluster shared volumes",
        "Use ReFS for Storage Spaces Direct deployments for better resilience and performance",
        "Use NTFS for classical storage configurations",
        "Implement appropriate storage redundancy (RAID, mirroring, etc.)",
        "Ensure at least one CSV per host for balanced resource allocation"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")

def render_storage_configuration():
    """
    Render the storage configuration page with modular components.
    
    This function organizes the storage configuration interface, including:
    - Storage architecture selection
    - Redundancy and MPIO options
    - Filesystem selection
    - CSV volume configuration
    - Storage validation and visualization
    """
    st.title("Storage Configuration")
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    # Display appropriate introduction text
    st.write(_get_intro_text(deployment_type))
    
    # Initialize storage configuration
    _initialize_storage_config()
    
    # Storage Architecture
    st.header("Storage Architecture")
    
    # Get number of Hyper-V hosts from hardware configuration
    hyper_v_hosts = st.session_state.configuration.get("hardware", {}).get("host_count", 2)
    
    # Render storage type selection
    storage_type, storage_connectivity, is_s2d = _render_storage_type_selection(hyper_v_hosts)
    
    # Render redundancy options
    redundancy, mpio_enabled = _render_redundancy_options(is_s2d)
    
    # Render filesystem options and CSV count
    filesystem, csv_count = _render_filesystem_options(is_s2d, hyper_v_hosts)
    
    # Additional options before CSV configuration
    shared_between_clusters = st.checkbox(
        "Storage shared between clusters",
        value=False,
        help="Not recommended: Share storage between different clusters"
    )
    
    if shared_between_clusters:
        st.warning("⚠️ Sharing storage between different clusters is not recommended.")
        
    # Storage Estimation Helper
    with st.expander("Storage Estimator", expanded=False):
        st.subheader("Estimate your storage needs")
        storage_recommendations = _render_storage_estimator()
        
        # Apply recommendations button
        if st.button("Apply Recommendations"):
            # Copy recommendations to the main configuration
            quorum_disk = storage_recommendations["quorum_disk"]
            csv_volumes = storage_recommendations["csv_volumes"]
            st.success("Recommendations applied to the configuration.")
    
    # Quorum Disk Configuration
    st.header("Quorum Disk Configuration")
    quorum_disk = _render_quorum_disk_config()
    
    # CSV Volumes Configuration
    st.header("Cluster Shared Volumes (CSV)")
    
    # Generate CSV volume configurations
    csv_volumes = _render_csv_configurations(csv_count, filesystem, redundancy)
    
    # Storage summary and validation
    storage_summary = _render_storage_summary(quorum_disk, csv_volumes)
    validation_results = _validate_storage_config(storage_type, csv_volumes, quorum_disk, 
                                                mpio_enabled, shared_between_clusters, 
                                                redundancy, hyper_v_hosts)
    
    # Storage visualization
    _render_storage_visualization(storage_type, csv_volumes, quorum_disk, mpio_enabled, 
                                shared_between_clusters, redundancy, hyper_v_hosts)
                                
    # Display best practices
    _render_storage_best_practices()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: Network Configuration", key="prev_network"):
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        next_button = st.button("Next: Security Settings", key="next_security")
        if next_button:
            if not validation_results["status"]:
                st.error("Please correct the storage configuration errors before proceeding.")
            else:
                _save_storage_configuration(
                    storage_type, csv_volumes, csv_count, quorum_disk, mpio_enabled,
                    shared_between_clusters, redundancy, storage_connectivity, 
                    filesystem, is_s2d, hyper_v_hosts
                )