import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.storage_validator import (
    validate_storage_configuration,
    create_storage_visualization,
    estimate_storage_needs
)

def render_storage_configuration():
    """Render the storage configuration page."""
    st.title("Storage Configuration")
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    if deployment_type == "hyperv":
        st.write("Configure the storage settings for your Hyper-V cluster. Proper storage setup is essential for cluster shared volumes, VM storage, and high availability.")
    else:
        st.write("Configure the storage settings for your Hyper-V cluster with SCVMM. Proper storage setup is essential for cluster shared volumes, VM storage, SCVMM library, and high availability.")
    
    # Initialize storage configuration in session state if not present
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "storage" not in st.session_state.configuration:
        st.session_state.configuration["storage"] = {
            "storage_type": "SAN",
            "csv_volumes": [{"size_gb": 1000, "purpose": "VM Storage"}],
            "quorum_disk": {"size_gb": 1},
            "mpio_enabled": True
        }
    
    # Function to update session state when storage configuration is confirmed
    def confirm_storage_configuration():
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
    
    # Storage Architecture
    st.header("Storage Architecture")
    
    # Get number of Hyper-V hosts from hardware configuration
    hyper_v_hosts = st.session_state.configuration.get("hardware", {}).get("host_count", 2)
    
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
    
    # Storage settings
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
            
    # Filesystem selection based on storage type
    col1, col2 = st.columns(2)
    
    with col1:
        if is_s2d:
            # For S2D, ReFS is recommended
            filesystem = st.selectbox(
                "Filesystem",
                options=["ReFS", "NTFS"],
                index=0,
                help="ReFS is recommended for S2D deployments"
            )
            if filesystem == "ReFS":
                st.success("✅ ReFS is the recommended filesystem for Storage Spaces Direct")
        else:
            # For classical storage, NTFS is recommended
            filesystem = st.selectbox(
                "Filesystem",
                options=["NTFS", "ReFS"],
                index=0,
                help="NTFS is recommended for classical storage"
            )
            if filesystem == "ReFS":
                st.warning("⚠️ ReFS is primarily recommended for Storage Spaces Direct. NTFS is the standard for classical storage.")
    
    with col2:
        # CSV per host recommendation
        min_csv_count = max(hyper_v_hosts, 1)  # At least one CSV per host
        csv_count = st.number_input(
            "Number of CSV volumes",
            min_value=min_csv_count,
            value=min_csv_count,
            help=f"Minimum recommended: At least one CSV per host ({hyper_v_hosts} hosts)"
        )
        
        if csv_count < hyper_v_hosts:
            st.warning(f"⚠️ It's recommended to have at least one CSV per host ({hyper_v_hosts} hosts)")
        else:
            st.success(f"✅ Good! You have at least one CSV per host ({csv_count} CSVs for {hyper_v_hosts} hosts)")
    
    
    shared_between_clusters = st.checkbox(
        "Storage shared between clusters",
        value=False,
        help="Not recommended: Share storage between different clusters"
    )
    
    if shared_between_clusters:
        st.warning("Sharing storage between different clusters is not recommended.")
    
    # Storage Estimation Helper
    st.header("Storage Estimation")
    
    with st.expander("Storage Estimator", expanded=False):
        st.subheader("Estimate your storage needs")
        
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
        
        # Apply recommendations button
        if st.button("Apply Recommendations"):
            # Copy recommendations to the main configuration
            quorum_disk = storage_recommendations["quorum_disk"]
            csv_volumes = storage_recommendations["csv_volumes"]
            st.success("Recommendations applied to the configuration.")
    
    # Quorum Disk Configuration
    st.header("Quorum Disk Configuration")
    
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
    
    # CSV Volumes Configuration
    st.header("Cluster Shared Volumes (CSV)")
    
    # Allow configuration of CSV volumes
    csv_volumes = []
    
    # Initial volume
    with st.expander("CSV Volume 1", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            csv1_size = st.number_input(
                "Volume Size (GB)",
                min_value=100,
                value=1000,
                help="Enter the size of the CSV volume in GB"
            )
        
        with col2:
            csv1_purpose = st.text_input(
                "Purpose",
                value="VM Storage",
                help="Enter the purpose of this volume"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv1_format = st.selectbox(
                "File System",
                options=["NTFS", "ReFS"],
                index=0,
                help="ReFS is recommended for new deployments"
            )
        
        with col2:
            csv1_redundancy = st.selectbox(
                "Volume Redundancy",
                options=["Same as Storage", "RAID 1", "RAID 5", "RAID 6", "RAID 10", "None"],
                index=0
            )
        
        # Add to CSV volumes
        csv_volumes.append({
            "size_gb": csv1_size,
            "purpose": csv1_purpose,
            "format": csv1_format,
            "redundancy": csv1_redundancy if csv1_redundancy != "Same as Storage" else redundancy
        })
    
    # Allow adding more volumes
    additional_volumes = st.number_input(
        "Additional CSV Volumes",
        min_value=0,
        max_value=10,
        value=1,
        help="Enter the number of additional CSV volumes to configure"
    )
    
    for i in range(additional_volumes):
        with st.expander(f"CSV Volume {i+2}"):
            col1, col2 = st.columns(2)
            
            with col1:
                csv_size = st.number_input(
                    "Volume Size (GB)",
                    min_value=100,
                    value=1000,
                    key=f"csv_size_{i}"
                )
            
            with col2:
                csv_purpose = st.text_input(
                    "Purpose",
                    value=f"VM Storage {i+2}",
                    key=f"csv_purpose_{i}"
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv_format = st.selectbox(
                    "File System",
                    options=["NTFS", "ReFS"],
                    index=0,
                    key=f"csv_format_{i}"
                )
            
            with col2:
                csv_redundancy = st.selectbox(
                    "Volume Redundancy",
                    options=["Same as Storage", "RAID 1", "RAID 5", "RAID 6", "RAID 10", "None"],
                    index=0,
                    key=f"csv_redundancy_{i}"
                )
            
            # Add to CSV volumes
            csv_volumes.append({
                "size_gb": csv_size,
                "purpose": csv_purpose,
                "format": csv_format,
                "redundancy": csv_redundancy if csv_redundancy != "Same as Storage" else redundancy
            })
    
    # Summary of storage configuration
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
    
    # Storage validation
    st.header("Storage Configuration Validation")
    
    # Compile configuration for validation
    storage_config = {
        "storage_type": storage_type,
        "csv_volumes": csv_volumes,
        "quorum_disk": quorum_disk,
        "mpio_enabled": mpio_enabled,
        "shared_between_clusters": shared_between_clusters,
        "redundancy": redundancy,
        "host_count": hyper_v_hosts
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
    
    # Storage visualization
    st.subheader("Storage Architecture Visualization")
    
    # Create storage visualization
    fig = create_storage_visualization(storage_config)
    st.plotly_chart(fig)
    
    # Storage best practices
    st.header("Storage Best Practices")
    
    best_practices = [
        "Use shared storage for all cluster nodes",
        "Implement MPIO for redundant storage connectivity",
        "Use small (1-5 GB) LUN for quorum disk",
        "Do not share storage between different clusters",
        "Consider using multiple CSV volumes for better performance and management",
        "Place only highly available VMs on cluster shared volumes",
        "Use ReFS for new deployments for better resilience and performance with VMs",
        "Implement appropriate storage redundancy (RAID, mirroring, etc.)"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")
    
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
                confirm_storage_configuration()
