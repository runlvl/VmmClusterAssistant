import plotly.graph_objects as go
import pandas as pd
import networkx as nx
import re
import math

def validate_ha_configuration(config):
    """
    Validate a high availability configuration dictionary.
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
        "enabled", 
        "cluster"
    ]
    
    for field in required_fields:
        if field not in config:
            results["errors"].append(f"Missing required high availability configuration: {field}")
            results["status"] = False
    
    if not results["status"]:
        return results
    
    # Validate cluster configuration if enabled
    if config["enabled"]:
        cluster_fields = ["name", "node_count", "quorum_type", "witness_type"]
        
        for field in cluster_fields:
            if field not in config["cluster"]:
                results["errors"].append(f"Missing required cluster configuration: {field}")
                results["status"] = False
        
        # Validate node count
        if "node_count" in config["cluster"]:
            node_count = config["cluster"]["node_count"]
            if node_count < 2:
                results["errors"].append("Cluster requires at least 2 nodes")
                results["status"] = False
            elif node_count > 64:
                results["warnings"].append("Large clusters (>16 nodes) may have performance implications")
                
        # Check if VMM is used, and if so validate VMM-specific fields
        if "use_vmm" in config and config["use_vmm"]:
            # Check VMM-specific required fields when VMM is enabled
            vmm_required_fields = ["vmm_service_account"]
            for field in vmm_required_fields:
                if field not in config or not config[field]:
                    results["errors"].append(f"Missing required VMM configuration: {field}")
                    results["status"] = False
        
        # Validate quorum type
        if "quorum_type" in config["cluster"]:
            valid_quorum_types = ["NodeMajority", "NodeAndDiskMajority", "NodeAndFileShareMajority", "NodeAndCloudWitness"]
            if config["cluster"]["quorum_type"] not in valid_quorum_types:
                results["warnings"].append(f"Quorum type '{config['cluster']['quorum_type']}' is not a standard quorum type")
        
        # Validate witness type
        if "witness_type" in config["cluster"]:
            valid_witness_types = ["DiskWitness", "FileShareWitness", "CloudWitness"]
            if config["cluster"]["witness_type"] not in valid_witness_types:
                results["warnings"].append(f"Witness type '{config['cluster']['witness_type']}' is not a standard witness type")
        
        # Validate witness resource if applicable
        if "witness_type" in config["cluster"] and config["cluster"]["witness_type"] != "None":
            if "witness_resource" not in config["cluster"]:
                results["warnings"].append("Witness resource should be specified for the selected witness type")
    
    # VMM-specific validations only if VMM is being used
    if "use_vmm" in config and config["use_vmm"]:
        # Validate VMM service account
        if "vmm_service_account" in config:
            account = config["vmm_service_account"]
            
            # Check domain format (domain\user)
            if account and "\\" not in account and "@" not in account:
                results["warnings"].append("VMM service account should be in domain\\username or username@domain format")
        
        # Validate library high availability
        if "library_ha" in config and config["library_ha"]:
            if "library_share" not in config:
                results["warnings"].append("High availability library share should be specified")
        
        # Add VMM-specific recommendations based on best practices
        if "vmm_db_ha" not in config or not config["vmm_db_ha"]:
            results["recommendations"].append("Configure high availability for the VMM database")
        
        if "dkm_enabled" not in config or not config["dkm_enabled"]:
            results["recommendations"].append("Configure Distributed Key Management for HA VMM environments")
        
        if "library_ha" not in config or not config["library_ha"]:
            results["recommendations"].append("Configure highly available VMM library")
    
    # General HA recommendations (regardless of VMM)
    if not config.get("enabled", False):
        results["recommendations"].append("Enable high availability for production environments")
    
    # If node count is low, recommend additional nodes
    if "cluster" in config and "node_count" in config["cluster"] and config["cluster"]["node_count"] < 3:
        results["recommendations"].append("Add additional nodes to the cluster for better availability")
    
    return results

def validate_service_account(account):
    """
    Validate a service account string.
    Returns a dictionary with validation results.
    """
    results = {
        "status": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    if not account:
        results["errors"].append("Service account cannot be empty")
        results["status"] = False
        return results
    
    # Check domain format (domain\user or user@domain)
    if "\\" in account:
        domain, username = account.split("\\", 1)
        
        if not domain:
            results["errors"].append("Domain name cannot be empty")
            results["status"] = False
        
        if not username:
            results["errors"].append("Username cannot be empty")
            results["status"] = False
        elif len(username) < 3:
            results["warnings"].append("Username should be at least 3 characters long")
    elif "@" in account:
        username, domain = account.split("@", 1)
        
        if not username:
            results["errors"].append("Username cannot be empty")
            results["status"] = False
        elif len(username) < 3:
            results["warnings"].append("Username should be at least 3 characters long")
        
        if not domain:
            results["errors"].append("Domain name cannot be empty")
            results["status"] = False
        
        # Validate domain format
        if domain and not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            results["warnings"].append("Domain format appears to be invalid")
    else:
        results["errors"].append("Service account should be in domain\\username or username@domain format")
        results["status"] = False
    
    # Check for service account best practices
    if "admin" in account.lower():
        results["warnings"].append("Avoid using 'admin' in service account names for security")
    
    if account.lower().startswith("administrator"):
        results["warnings"].append("Do not use built-in Administrator account for services")
    
    results["recommendations"].append("Ensure service account has the minimum required permissions")
    results["recommendations"].append("Consider using a managed service account (MSA) for improved security")
    
    return results

def create_ha_visualization(config):
    """
    Create a visual representation of the high availability configuration.
    Returns a Plotly figure.
    """
    # Create a graph
    G = nx.Graph()
    
    # Add nodes based on configuration
    nodes = []
    
    # Add cluster nodes
    node_count = config.get("cluster", {}).get("node_count", 2)
    for i in range(node_count):
        nodes.append(f"Node{i+1}")
        G.add_node(f"Node{i+1}")
    
    # Add shared cluster resources
    G.add_node("Cluster Service")
    
    # Add VMM-specific resources if VMM is used
    if config.get("use_vmm", False):
        G.add_node("VMM Service")
        G.add_node("SQL Database")
        
        # Add library if HA configured with VMM
        if config.get("library_ha", False):
            G.add_node("HA Library")
    
    # Add witness if applicable
    witness_type = config.get("cluster", {}).get("witness_type", None)
    if witness_type and witness_type != "None":
        G.add_node(f"{witness_type}")
    
    # Add edges (connections)
    for node in nodes:
        # All nodes connect to cluster service
        G.add_edge(node, "Cluster Service")
        
        # VMM-specific connections
        if config.get("use_vmm", False):
            G.add_edge(node, "VMM Service")
            G.add_edge(node, "SQL Database")
            
            if config.get("library_ha", False):
                G.add_edge(node, "HA Library")
        
        # Witness connection if applicable
        if witness_type and witness_type != "None":
            G.add_edge(node, f"{witness_type}")
    
    # Create positions for better visualization
    pos = {}
    
    # Position nodes in a circle
    angle_step = 2 * 3.14159 / node_count
    radius = 3
    
    for i in range(node_count):
        angle = i * angle_step
        pos[f"Node{i+1}"] = [radius * 1.5 * math.cos(angle), radius * math.sin(angle)]
    
    # Position cluster service in the center
    pos["Cluster Service"] = [0, 0]
    
    # Position VMM-specific resources if used
    if config.get("use_vmm", False):
        pos["VMM Service"] = [0, -1.5]
        pos["SQL Database"] = [0, -2.5]
        
        if config.get("library_ha", False):
            pos["HA Library"] = [-2, -1]
    
    # Position witness if applicable
    if witness_type and witness_type != "None":
        pos[f"{witness_type}"] = [2, -1]
    
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
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create node traces with different colors per type
    node_trace_cluster = go.Scatter(
        x=[pos[node][0] for node in G.nodes() if node.startswith("Node")],
        y=[pos[node][1] for node in G.nodes() if node.startswith("Node")],
        text=[node for node in G.nodes() if node.startswith("Node")],
        mode='markers+text',
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            color='#1f77b4',  # Blue for cluster nodes
            size=30,
            line_width=2
        )
    )
    
    # Set up the services to include in the visualization
    vmm_services = []
    if config.get("use_vmm", False):
        vmm_services = ["VMM Service", "SQL Database"]
    
    # Cluster service visualization
    node_trace_cluster_service = go.Scatter(
        x=[pos["Cluster Service"][0]],
        y=[pos["Cluster Service"][1]],
        text=["Cluster Service"],
        mode='markers+text',
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            color='#1C5631',  # Bechtle green for cluster service
            size=35,
            line_width=2
        )
    )
    
    # VMM services visualization (only if VMM is used)
    node_trace_services = go.Scatter(
        x=[pos[node][0] for node in G.nodes() if node in vmm_services],
        y=[pos[node][1] for node in G.nodes() if node in vmm_services],
        text=[node for node in G.nodes() if node in vmm_services],
        mode='markers+text',
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            color='#2ca02c',  # Green for services
            size=35,
            line_width=2
        )
    )
    
    # Other resources (witness, library)
    other_resources = []
    for node in G.nodes():
        if (node not in vmm_services and 
            node != "Cluster Service" and 
            not node.startswith("Node")):
            other_resources.append(node)
    
    node_trace_other = go.Scatter(
        x=[pos[node][0] for node in other_resources],
        y=[pos[node][1] for node in other_resources],
        text=other_resources,
        mode='markers+text',
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            color='#ff7f0e',  # Orange for other resources
            size=30,
            line_width=2
        )
    )
    
    # Create the figure with all traces
    traces = [edge_trace, node_trace_cluster, node_trace_cluster_service]
    
    # Only add services trace if VMM is used and there are services to show
    if config.get("use_vmm", False) and vmm_services:
        traces.append(node_trace_services)
    
    # Only add other resources trace if there are other resources to show
    if other_resources:
        traces.append(node_trace_other)
    
    # Use a cluster-focused title
    cluster_name = config.get('cluster', {}).get('name', 'Hyper-V Cluster')
    
    fig = go.Figure(data=traces,
                   layout=go.Layout(
                       title=f"High Availability Configuration: {cluster_name}",
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600,
                       width=800,
                       plot_bgcolor='rgba(240,240,240,0.8)'  # Light gray background
                   ))
    
    # Add annotations for quorum information
    quorum_type = config.get("cluster", {}).get("quorum_type", "Not specified")
    fig.add_annotation(
        x=pos["Cluster Service"][0],
        y=pos["Cluster Service"][1] - 0.7,
        text=f"Quorum Type: {quorum_type}",
        showarrow=False,
        font=dict(size=12)
    )
    
    return fig

def estimate_ha_requirements(node_count):
    """
    Estimate resource requirements for high availability setup.
    Returns a dictionary with recommendations.
    """
    requirements = {
        "servers": [],
        "storage": {},
        "network": {},
        "recommendations": []
    }
    
    # Server recommendations
    for i in range(node_count):
        requirements["servers"].append({
            "name": f"Node{i+1}",
            "cpu_cores": max(8, 4 * (i % 2 + 1)),  # Vary between 4 and 8 cores minimum
            "memory_gb": max(16, 8 * (i % 2 + 2)),  # Vary between 16 and 24 GB minimum
            "os_disk_gb": 100,
            "network_adapters": 4  # Minimum recommended for HA
        })
    
    # Storage recommendations
    requirements["storage"] = {
        "quorum_disk_gb": 1,
        "csv_volumes": [
            {"name": "CSV1", "size_gb": 500, "purpose": "VM Storage"},
            {"name": "CSV2", "size_gb": 500, "purpose": "VM Storage"},
        ],
        "witness_type": "Disk",
        "mpio_required": True
    }
    
    # Network recommendations
    requirements["network"] = {
        "dedicated_networks": True,
        "management_network": {"bandwidth": "1 Gbps", "redundant": True},
        "cluster_network": {"bandwidth": "10 Gbps", "redundant": True},
        "live_migration_network": {"bandwidth": "10 Gbps", "redundant": True},
        "vm_network": {"bandwidth": "10 Gbps", "redundant": True}
    }
    
    # General recommendations
    requirements["recommendations"] = [
        "Use identical hardware for all cluster nodes",
        "Configure at least two separate networks for cluster communication",
        "Enable redundant networking for all communication types",
        "Use a dedicated disk or file share for the cluster quorum witness",
        "Plan for N+1 capacity to handle node failures",
        "Test failover scenarios regularly",
        "Document failover procedures for administrators"
    ]
    
    return requirements
