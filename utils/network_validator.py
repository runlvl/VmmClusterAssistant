import ipaddress
import socket
import subprocess
import os
import plotly.graph_objects as go
import pandas as pd
import networkx as nx

def validate_ip_address(ip):
    """
    Validate an IP address.
    Returns a tuple of (is_valid, message).
    """
    try:
        ipaddress.ip_address(ip)
        return True, "Valid IP address"
    except ValueError:
        return False, "Invalid IP address format"

def validate_subnet_mask(subnet):
    """
    Validate a subnet mask.
    Returns a tuple of (is_valid, message).
    """
    try:
        ipaddress.IPv4Network(f"0.0.0.0/{subnet}", strict=False)
        return True, "Valid subnet mask"
    except ValueError:
        return False, "Invalid subnet mask"

def validate_cidr(cidr):
    """
    Validate a CIDR notation network.
    Returns a tuple of (is_valid, message).
    """
    try:
        ipaddress.ip_network(cidr)
        return True, "Valid CIDR notation"
    except ValueError:
        return False, "Invalid CIDR notation"

def ping_host(host):
    """
    Check if a host is reachable via ping.
    Returns a tuple of (is_reachable, message).
    """
    param = "-n" if os.name == "nt" else "-c"
    command = ["ping", param, "1", host]
    
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        if "TTL=" in output or "ttl=" in output:
            return True, "Host is reachable"
        else:
            return False, "Host does not respond to ping"
    except subprocess.CalledProcessError:
        return False, "Failed to reach host"
    except Exception as e:
        return False, f"Error: {str(e)}"

def resolve_hostname(hostname):
    """
    Resolve a hostname to an IP address.
    Returns a tuple of (is_resolved, result).
    Result can be an IP address or an error message.
    """
    try:
        ip = socket.gethostbyname(hostname)
        return True, ip
    except socket.gaierror:
        return False, "Hostname cannot be resolved"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_port_open(host, port):
    """
    Check if a specific port is open on a host.
    Returns a tuple of (is_open, message).
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, f"Port {port} is open"
        else:
            return False, f"Port {port} is closed"
    except socket.error as e:
        return False, f"Error checking port: {str(e)}"

def validate_network_configuration(config):
    """
    Validate a network configuration dictionary.
    Returns a dictionary with validation results.
    """
    results = {
        "status": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check required fields
    required_fields = [
        "management_network", 
        "migration_network", 
        "vm_network"
    ]
    
    for field in required_fields:
        if field not in config:
            results["status"] = False
            results["errors"].append(f"Missing required network configuration: {field}")
    
    if not results["status"]:
        return results
    
    # Validate management network
    mgmt_net = config["management_network"]
    if "cidr" in mgmt_net:
        valid, msg = validate_cidr(mgmt_net["cidr"])
        if not valid:
            results["status"] = False
            results["errors"].append(f"Management network CIDR invalid: {msg}")
    
    # Validate migration network
    mig_net = config["migration_network"]
    if "cidr" in mig_net:
        valid, msg = validate_cidr(mig_net["cidr"])
        if not valid:
            results["status"] = False
            results["errors"].append(f"Migration network CIDR invalid: {msg}")
    
    # Validate VM network
    vm_net = config["vm_network"]
    if "cidr" in vm_net:
        valid, msg = validate_cidr(vm_net["cidr"])
        if not valid:
            results["status"] = False
            results["errors"].append(f"VM network CIDR invalid: {msg}")
    
    # Check for network overlap
    networks = []
    for net_type, net_config in config.items():
        if isinstance(net_config, dict) and "cidr" in net_config:
            try:
                networks.append((net_type, ipaddress.ip_network(net_config["cidr"])))
            except ValueError:
                # Already caught above
                pass
    
    for i, (type1, net1) in enumerate(networks):
        for j, (type2, net2) in enumerate(networks):
            if i != j and (net1.overlaps(net2) or net2.overlaps(net1)):
                results["warnings"].append(f"Network overlap detected between {type1} and {type2}")
    
    # Add recommendations based on best practices
    if "dedicated_nics" not in config or not config["dedicated_nics"]:
        results["recommendations"].append("Use dedicated NICs for different network types (management, migration, VM)")
    
    if "ipsec" not in config or not config["ipsec"]:
        results["recommendations"].append("Enable IPsec on the Live Migration network for encrypted data transfer")
    
    if "separate_networks" not in config or not config["separate_networks"]:
        results["recommendations"].append("Use separate physical networks for management, VM traffic, and live migration")
    
    return results

def create_network_visualization(config):
    """
    Create a visual representation of the network configuration.
    Returns a Plotly figure.
    """
    # Create a graph
    G = nx.Graph()
    
    # Define nodes
    nodes = ["VMM Server", "SQL Server"]
    
    # Add Hyper-V hosts
    host_count = config.get("hyper_v_hosts", 2)
    for i in range(host_count):
        nodes.append(f"Hyper-V Host {i+1}")
    
    # Add network types
    networks = ["Management Network", "Migration Network", "VM Network"]
    nodes.extend(networks)
    
    # Add all nodes to the graph
    for node in nodes:
        G.add_node(node)
    
    # Add edges
    edges = []
    
    # Connect VMM and SQL to Management Network
    edges.append(("VMM Server", "Management Network"))
    edges.append(("SQL Server", "Management Network"))
    
    # Connect all Hyper-V hosts to networks
    for i in range(host_count):
        host_name = f"Hyper-V Host {i+1}"
        edges.append((host_name, "Management Network"))
        edges.append((host_name, "Migration Network"))
        edges.append((host_name, "VM Network"))
    
    G.add_edges_from(edges)
    
    # Create positions for better visualization
    pos = {
        "VMM Server": [-1, 2],
        "SQL Server": [1, 2],
        "Management Network": [0, 1],
        "Migration Network": [-2, 0],
        "VM Network": [2, 0]
    }
    
    # Position Hyper-V hosts
    for i in range(host_count):
        pos[f"Hyper-V Host {i+1}"] = [-1 + 2 * (i % 2), -1 - (i // 2)]
    
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
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
        # Set colors based on node type
        if "Network" in node:
            node_colors.append('#ff7f0e')  # Orange for networks
            node_sizes.append(35)
        elif "Host" in node:
            node_colors.append('#2ca02c')  # Green for Hyper-V hosts
            node_sizes.append(30)
        else:
            node_colors.append('#1f77b4')  # Blue for servers
            node_sizes.append(30)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_sizes,
            line_width=2))
    
    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title="Network Configuration",
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600,
                       plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)',
                   ))
    
    # Add annotations to show network details
    if "management_network" in config and "cidr" in config["management_network"]:
        fig.add_annotation(
            x=pos["Management Network"][0],
            y=pos["Management Network"][1] + 0.2,
            text=f"CIDR: {config['management_network']['cidr']}",
            showarrow=False,
            font=dict(size=10)
        )
    
    if "migration_network" in config and "cidr" in config["migration_network"]:
        fig.add_annotation(
            x=pos["Migration Network"][0],
            y=pos["Migration Network"][1] + 0.2,
            text=f"CIDR: {config['migration_network']['cidr']}",
            showarrow=False,
            font=dict(size=10)
        )
    
    if "vm_network" in config and "cidr" in config["vm_network"]:
        fig.add_annotation(
            x=pos["VM Network"][0],
            y=pos["VM Network"][1] + 0.2,
            text=f"CIDR: {config['vm_network']['cidr']}",
            showarrow=False,
            font=dict(size=10)
        )
    
    return fig
