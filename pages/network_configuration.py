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

def render_network_configuration():
    """Render the network configuration page."""
    st.title("Network Configuration")
    
    st.write("Configure the network settings for your VMM cluster. Proper network setup is crucial for cluster communication, VM traffic, and live migration.")
    
    # Initialize network configuration in session state if not present
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
    
    # Function to update session state when network configuration is confirmed
    def confirm_network_configuration():
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
        st.session_state.current_step = 4  # Move to next step (storage configuration)
        st.rerun()
    
    # Network Architecture
    st.header("Network Architecture")
    
    # Get number of Hyper-V hosts from hardware configuration
    hyper_v_hosts = st.session_state.configuration.get("hardware", {}).get("host_count", 2)
    
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
    
    # Management Network Configuration
    st.subheader("Management Network")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mgmt_network_cidr = st.text_input(
            "Management Network CIDR",
            value="192.168.1.0/24",
            help="Enter the management network CIDR (e.g., 192.168.1.0/24)"
        )
        
        # Validate CIDR
        is_valid_mgmt_cidr, mgmt_cidr_msg = validate_cidr(mgmt_network_cidr)
        if not is_valid_mgmt_cidr:
            st.error(f"Invalid CIDR format: {mgmt_cidr_msg}")
    
    with col2:
        mgmt_network_vlan = st.number_input(
            "Management Network VLAN ID",
            min_value=0,
            max_value=4095,
            value=0,
            help="Enter the VLAN ID for the management network (0 for untagged)"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        mgmt_network_gateway = st.text_input(
            "Management Network Gateway",
            value="192.168.1.1",
            help="Enter the gateway IP for the management network"
        )
        
        # Validate gateway IP
        is_valid_mgmt_gw, mgmt_gw_msg = validate_ip_address(mgmt_network_gateway)
        if not is_valid_mgmt_gw:
            st.error(f"Invalid gateway IP: {mgmt_gw_msg}")
    
    with col2:
        mgmt_network_dns = st.text_input(
            "Management Network DNS",
            value="192.168.1.10",
            help="Enter the DNS server IP for the management network"
        )
        
        # Validate DNS IP
        is_valid_mgmt_dns, mgmt_dns_msg = validate_ip_address(mgmt_network_dns)
        if not is_valid_mgmt_dns:
            st.error(f"Invalid DNS IP: {mgmt_dns_msg}")
    
    # Create management network configuration
    management_network = {
        "cidr": mgmt_network_cidr,
        "vlan": mgmt_network_vlan,
        "gateway": mgmt_network_gateway,
        "dns": mgmt_network_dns,
        "ip_range": str(ipaddress.IPv4Network(mgmt_network_cidr, strict=False)) if is_valid_mgmt_cidr else "",
        "subnet": str(ipaddress.IPv4Network(mgmt_network_cidr, strict=False).netmask) if is_valid_mgmt_cidr else ""
    }
    
    # Live Migration Network
    st.subheader("Live Migration Network")
    
    col1, col2 = st.columns(2)
    
    with col1:
        migration_network_cidr = st.text_input(
            "Live Migration Network CIDR",
            value="192.168.2.0/24",
            help="Enter the live migration network CIDR (e.g., 192.168.2.0/24)"
        )
        
        # Validate CIDR
        is_valid_migration_cidr, migration_cidr_msg = validate_cidr(migration_network_cidr)
        if not is_valid_migration_cidr:
            st.error(f"Invalid CIDR format: {migration_cidr_msg}")
    
    with col2:
        migration_network_vlan = st.number_input(
            "Live Migration Network VLAN ID",
            min_value=0,
            max_value=4095,
            value=10,
            help="Enter the VLAN ID for the live migration network"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        ipsec_enabled = st.checkbox(
            "Enable IPsec for Live Migration",
            value=False,
            help="Recommended: Encrypt live migration traffic for enhanced security"
        )
    
    # Create migration network configuration
    migration_network = {
        "cidr": migration_network_cidr,
        "vlan": migration_network_vlan,
        "gateway": "",  # Live migration network typically doesn't need a gateway
        "ipsec": ipsec_enabled,
        "ip_range": str(ipaddress.IPv4Network(migration_network_cidr, strict=False)) if is_valid_migration_cidr else "",
        "subnet": str(ipaddress.IPv4Network(migration_network_cidr, strict=False).netmask) if is_valid_migration_cidr else ""
    }
    
    # VM Network
    st.subheader("VM Network")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vm_network_cidr = st.text_input(
            "VM Network CIDR",
            value="192.168.3.0/24",
            help="Enter the VM network CIDR (e.g., 192.168.3.0/24)"
        )
        
        # Validate CIDR
        is_valid_vm_cidr, vm_cidr_msg = validate_cidr(vm_network_cidr)
        if not is_valid_vm_cidr:
            st.error(f"Invalid CIDR format: {vm_cidr_msg}")
    
    with col2:
        vm_network_vlan = st.number_input(
            "VM Network VLAN ID",
            min_value=0,
            max_value=4095,
            value=20,
            help="Enter the VLAN ID for the VM network"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        vm_network_gateway = st.text_input(
            "VM Network Gateway",
            value="192.168.3.1",
            help="Enter the gateway IP for the VM network"
        )
        
        # Validate gateway IP
        is_valid_vm_gw, vm_gw_msg = validate_ip_address(vm_network_gateway)
        if not is_valid_vm_gw:
            st.error(f"Invalid gateway IP: {vm_gw_msg}")
    
    with col2:
        vm_network_dns = st.text_input(
            "VM Network DNS",
            value="192.168.3.10",
            help="Enter the DNS server IP for the VM network"
        )
        
        # Validate DNS IP
        is_valid_vm_dns, vm_dns_msg = validate_ip_address(vm_network_dns)
        if not is_valid_vm_dns:
            st.error(f"Invalid DNS IP: {vm_dns_msg}")
    
    # Create VM network configuration
    vm_network = {
        "cidr": vm_network_cidr,
        "vlan": vm_network_vlan,
        "gateway": vm_network_gateway,
        "dns": vm_network_dns,
        "ip_range": str(ipaddress.IPv4Network(vm_network_cidr, strict=False)) if is_valid_vm_cidr else "",
        "subnet": str(ipaddress.IPv4Network(vm_network_cidr, strict=False).netmask) if is_valid_vm_cidr else ""
    }
    
    # Cluster Network (heartbeat)
    st.subheader("Cluster Network (Heartbeat)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cluster_network_cidr = st.text_input(
            "Cluster Network CIDR",
            value="192.168.4.0/24",
            help="Enter the cluster heartbeat network CIDR (e.g., 192.168.4.0/24)"
        )
        
        # Validate CIDR
        is_valid_cluster_cidr, cluster_cidr_msg = validate_cidr(cluster_network_cidr)
        if not is_valid_cluster_cidr:
            st.error(f"Invalid CIDR format: {cluster_cidr_msg}")
    
    with col2:
        cluster_network_vlan = st.number_input(
            "Cluster Network VLAN ID",
            min_value=0,
            max_value=4095,
            value=30,
            help="Enter the VLAN ID for the cluster heartbeat network"
        )
    
    # Create cluster network configuration
    cluster_network = {
        "cidr": cluster_network_cidr,
        "vlan": cluster_network_vlan,
        "gateway": "",  # Cluster heartbeat network typically doesn't need a gateway
        "ip_range": str(ipaddress.IPv4Network(cluster_network_cidr, strict=False)) if is_valid_cluster_cidr else "",
        "subnet": str(ipaddress.IPv4Network(cluster_network_cidr, strict=False).netmask) if is_valid_cluster_cidr else ""
    }
    
    # Network adapters configuration
    st.header("Network Adapter Configuration")
    
    # Allow configuration of network adapters for hosts
    network_adapters = []
    
    # Get server names from hardware configuration
    server_names = []
    for server in st.session_state.configuration.get("hardware", {}).get("servers", []):
        server_names.append(server.get("name", f"Server{len(server_names)+1}"))
    
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
                    nic_speed = st.selectbox(
                        f"Speed",
                        options=["1 Gbps", "10 Gbps", "25 Gbps", "40 Gbps"],
                        index=1 if j > 0 else 0,  # Default 10 Gbps for all except first
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
    
    # Logical Networks Configuration
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
    
    # VM Networks
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
            with st.expander(f"Additional VM Network {i+1}"):
                vm_net_name = st.text_input(
                    "Network Name",
                    value=f"VM Network {i+1}",
                    key=f"vm_net_name_{i}"
                )
                
                vm_net_desc = st.text_input(
                    "Description",
                    value=f"Additional VM network {i+1}",
                    key=f"vm_net_desc_{i}"
                )
                
                vm_net_logical = st.selectbox(
                    "Logical Network",
                    options=["VM"],
                    index=0,
                    key=f"vm_net_logical_{i}"
                )
                
                vm_net_isolated = st.checkbox(
                    "Network Isolation",
                    value=True,
                    key=f"vm_net_isolated_{i}",
                    help="Use network virtualization to isolate this network"
                )
                
                # Add to VM networks
                vm_networks.append({
                    "name": vm_net_name,
                    "description": vm_net_desc,
                    "logical_network": vm_net_logical,
                    "isolated": vm_net_isolated
                })
    
    # Display VM networks
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
    
    # Network validation
    st.header("Network Configuration Validation")
    
    # Compile configuration for validation
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
    
    # Validate network configuration
    validation_results = validate_network_configuration(network_config)
    
    # Display validation results
    if not validation_results["status"]:
        st.error("Network configuration has errors that must be corrected.")
        for error in validation_results["errors"]:
            st.error(error)
    
    for warning in validation_results["warnings"]:
        st.warning(warning)
    
    for recommendation in validation_results["recommendations"]:
        st.info(f"Recommendation: {recommendation}")
    
    # Network visualization
    st.subheader("Network Architecture Visualization")
    
    # Create network visualization
    fig = create_network_visualization(network_config)
    st.plotly_chart(fig)
    
    # Network best practices
    st.header("Network Best Practices")
    
    best_practices = [
        "Use separate networks for different traffic types (management, live migration, VM)",
        "Configure NIC teaming for redundancy where appropriate",
        "Enable IPsec on the live migration network for security",
        "Use consistent network naming conventions across all hosts",
        "Configure QoS policies only if needed based on observed performance",
        "Ensure networks don't overlap with each other or existing networks",
        "Use VLANs to segment different traffic types when using shared physical infrastructure"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: Software Requirements", key="prev_software"):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        next_button = st.button("Next: Storage Configuration", key="next_storage")
        if next_button:
            if not validation_results["status"]:
                st.error("Please correct the network configuration errors before proceeding.")
            else:
                confirm_network_configuration()
