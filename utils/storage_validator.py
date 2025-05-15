import os
import plotly.graph_objects as go
import pandas as pd
import subprocess

def validate_storage_configuration(config):
    """
    Validate a storage configuration dictionary.
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
        "storage_type", 
        "csv_volumes",
        "quorum_disk"
    ]
    
    for field in required_fields:
        if field not in config:
            results["status"] = False
            results["errors"].append(f"Missing required storage configuration: {field}")
    
    if not results["status"]:
        return results
    
    # Validate storage type
    valid_storage_types = ["SAN", "SMB", "Local", "iSCSI", "FC", "NVMe"]
    if config["storage_type"] not in valid_storage_types:
        results["warnings"].append(f"Storage type '{config['storage_type']}' is not a common VMM storage type")
    
    # Validate CSV volumes
    if len(config["csv_volumes"]) == 0:
        results["errors"].append("At least one CSV volume must be defined")
        results["status"] = False
    
    for i, volume in enumerate(config["csv_volumes"]):
        if "size_gb" not in volume:
            results["warnings"].append(f"CSV volume {i+1} is missing size information")
        elif volume["size_gb"] < 100:
            results["warnings"].append(f"CSV volume {i+1} is smaller than recommended (100 GB minimum)")
    
    # Validate quorum disk
    if "size_gb" not in config["quorum_disk"]:
        results["warnings"].append("Quorum disk is missing size information")
    elif config["quorum_disk"]["size_gb"] < 1 or config["quorum_disk"]["size_gb"] > 5:
        results["warnings"].append("Quorum disk size should be between 1 GB and 5 GB")
    
    # Add recommendations based on best practices
    if config["storage_type"] == "Local":
        results["recommendations"].append("Local storage is not recommended for production VMM clusters. Consider using shared storage.")
    
    if config.get("redundancy", "None") == "None":
        results["recommendations"].append("Implement storage redundancy (RAID, mirroring, etc.) for production environments")
    
    if len(config["csv_volumes"]) < 2:
        results["recommendations"].append("Consider using multiple CSV volumes for better performance and management")
    
    if not config.get("mpio_enabled", False):
        results["recommendations"].append("Enable Multipath I/O (MPIO) for redundant storage connectivity")
    
    # Check if storage is shared between clusters
    if config.get("shared_between_clusters", False):
        results["warnings"].append("Storage should not be shared between different clusters")
    
    return results

def create_storage_visualization(config):
    """
    Create a visual representation of the storage configuration.
    Returns a Plotly figure.
    """
    # Create nodes for the visualization
    nodes = [
        {"id": "Storage", "label": f"{config['storage_type']} Storage", "group": "storage"},
        {"id": "Quorum", "label": f"Quorum Disk\n{config['quorum_disk'].get('size_gb', 'N/A')} GB", "group": "quorum"}
    ]
    
    # Add CSV volumes
    for i, volume in enumerate(config["csv_volumes"]):
        size = volume.get("size_gb", "N/A")
        purpose = volume.get("purpose", "General")
        nodes.append({
            "id": f"CSV{i+1}",
            "label": f"CSV {i+1}\n{size} GB\n{purpose}",
            "group": "csv"
        })
    
    # Add hosts based on configuration
    host_count = config.get("host_count", 2)
    for i in range(host_count):
        nodes.append({
            "id": f"Host{i+1}",
            "label": f"Hyper-V Host {i+1}",
            "group": "host"
        })
    
    # Define edges for connections
    edges = []
    
    # Connect hosts to storage
    for i in range(host_count):
        edges.append({"from": f"Host{i+1}", "to": "Storage"})
    
    # Connect storage to volumes
    edges.append({"from": "Storage", "to": "Quorum"})
    for i in range(len(config["csv_volumes"])):
        edges.append({"from": "Storage", "to": f"CSV{i+1}"})
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    
    # Define positions
    positions = {
        "Storage": [0, 0],
        "Quorum": [0, -1.5]
    }
    
    # Position CSV volumes in a horizontal line below storage
    csv_count = len(config["csv_volumes"])
    for i in range(csv_count):
        offset = (i - (csv_count - 1) / 2) * 1.5
        positions[f"CSV{i+1}"] = [offset, -3]
    
    # Position hosts in a horizontal line above storage
    for i in range(host_count):
        offset = (i - (host_count - 1) / 2) * 2
        positions[f"Host{i+1}"] = [offset, 2]
    
    # Create node data
    for node in nodes:
        pos = positions[node["id"]]
        node_x.append(pos[0])
        node_y.append(pos[1])
        node_text.append(node["label"])
        
        # Set color based on group
        if node["group"] == "storage":
            node_colors.append('#ff7f0e')  # Orange for storage
            node_sizes.append(35)
        elif node["group"] == "quorum":
            node_colors.append('#d62728')  # Red for quorum
            node_sizes.append(25)
        elif node["group"] == "csv":
            node_colors.append('#2ca02c')  # Green for CSV
            node_sizes.append(30)
        else:  # host
            node_colors.append('#1f77b4')  # Blue for hosts
            node_sizes.append(30)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="middle center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_sizes,
            line_width=2))
    
    # Create edge trace
    edge_x = []
    edge_y = []
    
    for edge in edges:
        from_pos = positions[edge["from"]]
        to_pos = positions[edge["to"]]
        edge_x.extend([from_pos[0], to_pos[0], None])
        edge_y.extend([from_pos[1], to_pos[1], None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title="Storage Configuration",
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600,
                       width=800,
                       plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)',
                   ))
    
    # Add annotations for storage details
    fig.add_annotation(
        x=positions["Storage"][0],
        y=positions["Storage"][1] + 0.5,
        text=f"Type: {config['storage_type']}",
        showarrow=False,
        font=dict(size=12)
    )
    
    if config.get("mpio_enabled", False):
        fig.add_annotation(
            x=positions["Storage"][0],
            y=positions["Storage"][1] - 0.5,
            text="MPIO Enabled",
            showarrow=False,
            font=dict(size=10, color="green")
        )
    
    return fig

def estimate_storage_needs(vm_count, avg_vm_size_gb):
    """
    Estimate storage needs based on number of VMs and average VM size.
    Returns a dictionary with recommendations.
    """
    # Basic calculations
    total_vm_storage = vm_count * avg_vm_size_gb
    
    # Add overhead for VM configuration, checkpoints, etc. (20%)
    total_storage_with_overhead = total_vm_storage * 1.2
    
    # Quorum disk size
    quorum_size = 1  # GB, standard size
    
    # Determine number of CSV volumes based on size
    csv_count = max(2, int(total_storage_with_overhead / 2000) + 1)  # 2TB per CSV recommended max
    
    # Calculate CSV sizes (distribute evenly)
    csv_size = total_storage_with_overhead / csv_count
    
    recommendations = {
        "quorum_disk": {
            "size_gb": quorum_size,
            "purpose": "Cluster quorum"
        },
        "csv_volumes": []
    }
    
    # Create CSV volume recommendations
    for i in range(csv_count):
        recommendations["csv_volumes"].append({
            "size_gb": int(csv_size),
            "purpose": f"VM Storage {i+1}"
        })
    
    # Add buffer volume for future growth
    recommendations["csv_volumes"].append({
        "size_gb": int(total_storage_with_overhead * 0.2),
        "purpose": "Growth buffer"
    })
    
    # Add recommendations text
    recommendations["text"] = [
        f"Total VM storage required: {total_vm_storage} GB",
        f"With 20% overhead: {total_storage_with_overhead:.0f} GB",
        f"Recommended CSV count: {csv_count}",
        f"Recommended CSV size: {csv_size:.0f} GB each",
        "Consider implementing storage redundancy (RAID, mirroring)",
        "Enable MPIO for redundant storage connectivity"
    ]
    
    return recommendations
