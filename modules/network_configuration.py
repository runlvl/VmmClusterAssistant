import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import ipaddress
from utils.network_validator import (
    validate_ip_address, 
    validate_subnet_mask, 
    validate_cidr, 
    validate_network_configuration,
    create_network_visualization
)
from utils.navigation import go_to_software, go_to_storage

# Helper functions for network configuration

def _initialize_network_config():
    """Initialize network configuration in session state if not present."""
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "network" not in st.session_state.configuration:
        st.session_state.configuration["network"] = {
            "management_network": {},
            "migration_network": {},
            "vm_network": {},
            "cluster_network": {},
            "dedicated_nics": True,
            "ipsec": False,
            "separate_networks": True,
            "hyper_v_hosts": 2  # Default
        }

def _save_network_configuration(management_network, migration_network, vm_network, 
                             cluster_network, dedicated_nics, ipsec_enabled, 
                             separate_networks, hyper_v_hosts, network_adapters, 
                             logical_networks, vm_networks):
    """Save the network configuration to session state."""
    st.session_state.configuration["network"] = {
        "management_network": management_network,
        "migration_network": migration_network,
        "vm_network": vm_network,
        "cluster_network": cluster_network,
        "dedicated_nics": dedicated_nics,
        "ipsec": ipsec_enabled,
        "separate_networks": separate_networks,
        "hyper_v_hosts": hyper_v_hosts,
        "adapters": network_adapters,
        "logical_networks": logical_networks,
        "vm_networks": vm_networks
    }
    
    if "completed_steps" not in st.session_state:
        st.session_state.completed_steps = set()
    
    st.session_state.completed_steps.add(3)  # Mark network configuration step as completed
    st.session_state.current_step = 5  # Move to next step (storage configuration)

def _render_network_architecture_settings(storage_type):
    """Render network architecture settings UI component."""
    # Display recommendation info box based on storage type
    is_s2d = storage_type == "Storage Spaces Direct (S2D)"
    
    if is_s2d:
        st.info("💡 S2D storage detected - recommended network configuration: 2x2 25 Gbps NICs for optimal performance")
    else:
        st.info("💡 Recommended network configuration: 2x2 10 Gbps NICs (minimum)")
    
    # Network design decisions
    col1, col2 = st.columns(2)
    
    with col1:
        dedicated_nics = st.checkbox(
            "Use dedicated NICs for different networks", 
            value=True,
            help="Recommended: Use separate physical NICs for different network types"
        )
    
    with col2:
        separate_networks = st.checkbox(
            "Use separate networks for different traffic types", 
            value=True,
            help="Recommended: Separate management, VM, and live migration traffic"
        )
    
    if not dedicated_nics:
        st.warning("Using shared NICs for different network types may impact performance and security.")
    
    if not separate_networks:
        st.warning("Using the same network for different traffic types is not recommended for production environments.")
        
    return dedicated_nics, separate_networks, is_s2d

def _configure_network(network_type, default_cidr, default_vlan, need_gateway=True, need_dns=True):
    """Configure a specific network (management, migration, VM, or cluster)."""
    network_config = {}
    gateway = ""
    dns = ""
    
    col1, col2 = st.columns(2)
    
    with col1:
        network_cidr = st.text_input(
            f"{network_type} Network CIDR",
            value=default_cidr,
            help=f"Enter the {network_type.lower()} network CIDR (e.g., {default_cidr})"
        )
        
        # Validate CIDR
        is_valid_cidr, cidr_msg = validate_cidr(network_cidr)
        if not is_valid_cidr:
            st.error(f"Invalid CIDR format: {cidr_msg}")
    
    with col2:
        network_vlan = st.number_input(
            f"{network_type} Network VLAN ID",
            min_value=0,
            max_value=4095,
            value=default_vlan,
            help=f"Enter the VLAN ID for the {network_type.lower()} network"
        )
    
    # Add gateway and DNS if needed
    if need_gateway or need_dns:
        col1, col2 = st.columns(2)
        
        if need_gateway:
            with col1:
                gateway = st.text_input(
                    f"{network_type} Network Gateway",
                    value=default_cidr.rsplit('.', 1)[0] + ".1" if is_valid_cidr else "",
                    help=f"Enter the gateway IP for the {network_type.lower()} network"
                )
                
                # Validate gateway IP
                is_valid_gw, gw_msg = validate_ip_address(gateway)
                if not is_valid_gw:
                    st.error(f"Invalid gateway IP: {gw_msg}")
        
        if need_dns:
            with col2:
                dns = st.text_input(
                    f"{network_type} Network DNS",
                    value=default_cidr.rsplit('.', 1)[0] + ".10" if is_valid_cidr else "",
                    help=f"Enter the DNS server IP for the {network_type.lower()} network"
                )
                
                # Validate DNS IP
                is_valid_dns, dns_msg = validate_ip_address(dns)
                if not is_valid_dns:
                    st.error(f"Invalid DNS IP: {dns_msg}")
    
    # Create network configuration
    network_config = {
        "cidr": network_cidr,
        "vlan": network_vlan,
        "gateway": gateway if need_gateway else "",
        "dns": dns if need_dns else "",
        "ip_range": str(ipaddress.IPv4Network(network_cidr, strict=False)) if is_valid_cidr else "",
        "subnet": str(ipaddress.IPv4Network(network_cidr, strict=False).netmask) if is_valid_cidr else ""
    }
    
    return network_config

def _configure_migration_network(default_cidr="192.168.2.0/24", default_vlan=10):
    """Configure the Live Migration network specifically."""
    st.subheader("Live Migration Network")
    
    migration_network = _configure_network(
        "Live Migration", default_cidr, default_vlan, need_gateway=False, need_dns=False
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        ipsec_enabled = st.checkbox(
            "Enable IPsec for Live Migration",
            value=False,
            help="Recommended: Encrypt live migration traffic for enhanced security"
        )
    
    migration_network["ipsec"] = ipsec_enabled
    
    return migration_network, ipsec_enabled

def _configure_network_adapters(server_names, storage_type):
    """Configure network adapters for each server."""
    network_adapters = []
    is_s2d = storage_type == "Storage Spaces Direct (S2D)"
    
    # Network adapter configuration for each server
    for i, server_name in enumerate(server_names):
        with st.expander(f"Network Adapters for {server_name}", expanded=(i==0)):
            st.subheader(f"Network Adapters for {server_name}")
            
            # Get NIC count from hardware configuration if available
            nic_count = 4  # Default
            for server in st.session_state.configuration.get("hardware", {}).get("servers", []):
                if server.get("name") == server_name:
                    nic_count = server.get("nic_count", 4)
                    break
            
            for j in range(nic_count):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    nic_name = st.text_input(
                        f"NIC {j+1} Name",
                        value=f"{'Management' if j==0 else 'LiveMigration' if j==1 else 'VM' if j==2 else 'Cluster'}{j+1}",
                        key=f"nic_name_{i}_{j}"
                    )
                
                with col2:
                    nic_type = st.selectbox(
                        f"NIC {j+1} Type",
                        options=["Management", "Live Migration", "VM Network", "Cluster"],
                        index=min(j, 3),
                        key=f"nic_type_{i}_{j}"
                    )
                
                with col3:
                    # Default speeds based on storage type and network type
                    default_index = 0
                    speed_options = ["10 Gbps", "25 Gbps", "40 Gbps"]
                    
                    # For S2D, recommend 25 Gbps for storage/migration networks
                    if is_s2d and (nic_type == "Live Migration" or nic_type == "VM Network"):
                        default_index = 1
                    
                    nic_speed = st.selectbox(
                        f"Speed",
                        options=speed_options,
                        index=default_index,
                        key=f"nic_speed_{i}_{j}"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    nic_teaming = st.checkbox(
                        f"NIC Teaming",
                        value=False,
                        key=f"nic_teaming_{i}_{j}"
                    )
                
                # Add adapter to configuration
                network_adapters.append({
                    "server": server_name,
                    "name": nic_name,
                    "network_type": nic_type,
                    "speed": nic_speed,
                    "teaming": nic_teaming
                })
    
    return network_adapters

def _configure_logical_networks(management_network, migration_network, vm_network):
    """Configure VMM logical networks based on physical networks."""
    st.header("VMM Logical Networks")
    
    # Create logical networks based on the physical networks configured
    logical_networks = [
        {
            "name": "Management",
            "description": "Network for management traffic",
            "network_virtualization": False,
            "cidr": management_network["cidr"],
            "vlan": management_network["vlan"]
        },
        {
            "name": "LiveMigration",
            "description": "Network for live migration traffic",
            "network_virtualization": False,
            "cidr": migration_network["cidr"],
            "vlan": migration_network["vlan"]
        },
        {
            "name": "VM",
            "description": "Network for virtual machine traffic",
            "network_virtualization": True,
            "cidr": vm_network["cidr"],
            "vlan": vm_network["vlan"]
        }
    ]
    
    # Display logical networks
    st.subheader("Logical Networks")
    logical_networks_df = pd.DataFrame([
        {
            "Name": network["name"],
            "Description": network["description"],
            "CIDR": network["cidr"],
            "VLAN": network["vlan"],
            "Network Virtualization": "Enabled" if network["network_virtualization"] else "Disabled"
        }
        for network in logical_networks
    ])
    
    st.table(logical_networks_df)
    
    return logical_networks

def _configure_vm_networks():
    """Configure VMM VM networks."""
    st.subheader("VM Networks")
    
    # Define VM networks
    vm_networks = [
        {
            "name": "VM Network",
            "description": "Primary VM network",
            "logical_network": "VM",
            "isolated": False
        }
    ]
    
    # Allow adding more VM networks
    if st.checkbox("Add additional VM networks"):
        num_additional_networks = st.number_input(
            "Number of additional VM networks",
            min_value=1,
            max_value=5,
            value=1
        )
        
        for i in range(num_additional_networks):
            with st.expander(f"Additional VM Network {i+1}", expanded=(i==0)):
                network_name = st.text_input(
                    "VM Network Name",
                    value=f"VM Network {i+2}",
                    key=f"vm_network_name_{i}"
                )
                
                network_desc = st.text_input(
                    "VM Network Description",
                    value=f"Additional VM network {i+2}",
                    key=f"vm_network_desc_{i}"
                )
                
                network_isolated = st.checkbox(
                    "Isolated Network",
                    value=False,
                    key=f"vm_network_isolated_{i}",
                    help="Isolated networks cannot communicate with other networks"
                )
                
                vm_networks.append({
                    "name": network_name,
                    "description": network_desc,
                    "logical_network": "VM",
                    "isolated": network_isolated
                })
    
    # Display VM networks table
    vm_networks_df = pd.DataFrame([
        {
            "Name": network["name"],
            "Description": network["description"],
            "Logical Network": network["logical_network"],
            "Isolation": "Enabled" if network["isolated"] else "Disabled"
        }
        for network in vm_networks
    ])
    
    st.table(vm_networks_df)
    
    return vm_networks

def _display_validation_results(validation_results):
    """Display network validation results."""
    if validation_results["status"]:
        st.success("Network configuration is valid.")
    else:
        st.error("Network configuration has errors. Please review the issues below.")
    
    if validation_results["errors"]:
        st.subheader("Errors")
        for error in validation_results["errors"]:
            st.error(error)
    
    if validation_results["warnings"]:
        st.subheader("Warnings")
        for warning in validation_results["warnings"]:
            st.warning(warning)
    
    if validation_results["recommendations"]:
        st.subheader("Recommendations")
        for recommendation in validation_results["recommendations"]:
            st.info(recommendation)

def _display_network_best_practices():
    """Display network best practices."""
    st.header("Network Best Practices")
    
    best_practices = [
        "Use redundant NICs for all network types",
        "Leverage NIC teaming for fault tolerance",
        "Separate management, VM, and live migration traffic",
        "Use VLANs to isolate different network traffic",
        "Enable Quality of Service (QoS) for live migration and VM traffic",
        "Use at least 10 Gbps NICs for all networks",
        "Consider using 25 Gbps or faster NICs for storage traffic in S2D deployments",
        "Configure jumbo frames (MTU 9000) for storage and live migration networks",
        "Document your network topology and IP address assignments"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")

def validate_nic_speed_requirements(network_adapters, is_s2d=False):
    """
    Validate that NIC speed meets modern requirements.
    
    Args:
        network_adapters: List of configured network adapters
        is_s2d: Whether Storage Spaces Direct is used
        
    Returns:
        dict: Validation results containing status, errors, warnings, and recommendations
    """
    result = {
        "status": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Collect NIC speeds by server and network type
    server_nics = {}
    for adapter in network_adapters:
        server = adapter["server"]
        network_type = adapter["network_type"]
        speed = adapter["speed"]
        
        if server not in server_nics:
            server_nics[server] = {}
        
        if network_type not in server_nics[server]:
            server_nics[server][network_type] = []
        
        server_nics[server][network_type].append(speed)
    
    # Validate each server's NIC configuration
    for server, nic_config in server_nics.items():
        # Check for minimum 10 Gbps NICs
        has_slow_nics = False
        for network_type, speeds in nic_config.items():
            for speed in speeds:
                if "1 Gbps" in speed:
                    has_slow_nics = True
                    result["warnings"].append(f"Server {server} has a 1 Gbps NIC for {network_type}. 10 Gbps is the recommended minimum.")
        
        # Check for minimum 2 NICs per network type (redundancy)
        for network_type, speeds in nic_config.items():
            if len(speeds) < 2:
                result["warnings"].append(f"Server {server} has only {len(speeds)} NIC(s) for {network_type}. At least 2 NICs are recommended for redundancy.")
                
        # Check for S2D specific requirements (25 Gbps NICs for storage)
        if is_s2d:
            if "Live Migration" in nic_config:
                has_25gbps = False
                for speed in nic_config["Live Migration"]:
                    if "25 Gbps" in speed or "40 Gbps" in speed:
                        has_25gbps = True
                
                if not has_25gbps:
                    result["warnings"].append(f"Server {server} should have at least one 25 Gbps or faster NIC for Live Migration with S2D.")
                    result["recommendations"].append(f"For S2D deployments, configure at least 2x 25 Gbps NICs for Live Migration on server {server}.")
    
    # General recommendations based on overall configuration
    if is_s2d:
        result["recommendations"].append("For Storage Spaces Direct (S2D), it's recommended to have at least 2x2 25 Gbps NICs (2 for VM traffic, 2 for storage/migration).")
    else:
        result["recommendations"].append("For standard deployments, it's recommended to have at least 2x2 10 Gbps NICs (2 for VM traffic, 2 for storage/migration).")
    
    return result

def render_network_configuration():
    """Render the network configuration page."""
    st.title("Network Configuration")
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    if deployment_type == "hyperv":
        st.write("Configure the network settings for your Hyper-V cluster. Proper network setup is crucial for cluster communication, VM traffic, and live migration.")
    else:
        st.write("Configure the network settings for your Hyper-V cluster with SCVMM. Proper network setup is crucial for cluster communication, VM traffic, SCVMM management, and live migration.")
    
    # Initialize network configuration in session state if not present
    _initialize_network_config()
    
    # Network Architecture section
    st.header("Network Architecture")
    
    # Get number of Hyper-V hosts from hardware configuration
    hyper_v_hosts = st.session_state.configuration.get("hardware", {}).get("host_count", 2)
    
    # Get storage type if available
    storage_type = st.session_state.configuration.get("storage", {}).get("storage_type", "SAN")
    
    # Render network architecture settings and get the selected options
    dedicated_nics, separate_networks, is_s2d = _render_network_architecture_settings(storage_type)
    
    # Network configuration - using modular functions for each network type
    
    # Management Network
    st.subheader("Management Network")
    management_network = _configure_network("Management", "192.168.1.0/24", 0, need_gateway=True, need_dns=True)
    
    # Live Migration Network - using specific configuration function
    migration_network, ipsec_enabled = _configure_migration_network("192.168.2.0/24", 10)
    
    # VM Network
    st.subheader("VM Network")
    vm_network = _configure_network("VM", "192.168.3.0/24", 20, need_gateway=True, need_dns=True)
    
    # Cluster Network
    st.subheader("Cluster Network (Heartbeat)")
    cluster_network = _configure_network("Cluster", "192.168.4.0/24", 30, need_gateway=False, need_dns=False)
    
    # Network adapters configuration
    st.header("Network Adapter Configuration")
    
    # Get server names from hardware configuration
    server_names = []
    for server in st.session_state.configuration.get("hardware", {}).get("servers", []):
        server_names.append(server.get("name", f"Server{len(server_names)+1}"))
    
    # Configure network adapters using modular function
    network_adapters = _configure_network_adapters(server_names, storage_type)
    
    # Only show VMM logical networks configuration if deployment type includes SCVMM
    if deployment_type == "scvmm":
        # Configure logical networks for SCVMM
        logical_networks = _configure_logical_networks(management_network, migration_network, vm_network)
        
        # Configure VM networks for SCVMM
        vm_networks = _configure_vm_networks()
    else:
        # Set defaults for non-SCVMM deployments
        logical_networks = []
        vm_networks = []
    
    # Network Validation
    st.header("Network Validation")
    
    # Validate networks for conflicts
    network_config = {
        "management_network": management_network,
        "migration_network": migration_network,
        "vm_network": vm_network,
        "cluster_network": cluster_network,
        "dedicated_nics": dedicated_nics,
        "ipsec": ipsec_enabled,
        "separate_networks": separate_networks,
        "hyper_v_hosts": hyper_v_hosts
    }
    
    # Add storage type and custom speed requirements to validation
    network_config["is_s2d"] = is_s2d
    
    # Validate NIC speed based on storage type
    nic_speed_validation = validate_nic_speed_requirements(network_adapters, is_s2d)
    
    # Validate network configuration
    validation_results = validate_network_configuration(network_config)
    
    # Merge speed validation results into general validation results
    if not nic_speed_validation["status"]:
        validation_results["status"] = False
        validation_results["errors"].extend(nic_speed_validation["errors"])
    validation_results["warnings"].extend(nic_speed_validation["warnings"])
    validation_results["recommendations"].extend(nic_speed_validation["recommendations"])
    
    # Display validation results
    _display_validation_results(validation_results)
    
    # Network Visualization
    st.header("Network Visualization")
    fig = create_network_visualization(network_config)
    st.plotly_chart(fig)
    
    # Network Best Practices
    _display_network_best_practices()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Direct navigation to Software Requirements
        prev_button = st.button("← Software Requirements", use_container_width=True)
        if prev_button:
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        next_button = st.button("Storage Configuration →", use_container_width=True)
        if next_button:
            if not validation_results["status"]:
                st.error("Please correct the network configuration errors before proceeding.")
            else:
                _save_network_configuration(
                    management_network, migration_network, vm_network, cluster_network,
                    dedicated_nics, ipsec_enabled, separate_networks, hyper_v_hosts,
                    network_adapters, logical_networks, vm_networks
                )
                # Direct navigation to Storage Configuration
                st.session_state.current_step = 5
                st.rerun()