import os
import platform
import psutil
import socket
import subprocess
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def check_system_requirements():
    """
    Check if the current system meets the requirements for running the VMM Cluster Implementation Tool.
    Returns a dictionary with the status and information about the system.
    """
    system_info = {
        "status": True,
        "message": "System meets requirements",
        "os": {
            "name": platform.system(),
            "version": platform.version(),
            "release": platform.release()
        },
        "hardware": {
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_logical_count": psutil.cpu_count(logical=True),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2)
        },
        "network": {
            "hostname": socket.gethostname(),
            "ip_address": get_ip_address(),
            "interfaces": get_network_interfaces()
        },
        "storage": {
            "disks": get_disk_info()
        }
    }
    
    # Check requirements
    requirements = []
    
    # Check Python version
    python_version = platform.python_version()
    python_req = {"name": "Python version", "value": python_version, "required": "3.6+", "status": True}
    if int(python_version.split('.')[0]) < 3 or (int(python_version.split('.')[0]) == 3 and int(python_version.split('.')[1]) < 6):
        python_req["status"] = False
        system_info["status"] = False
        system_info["message"] = "Python version does not meet requirements"
    requirements.append(python_req)
    
    # Check CPU
    cpu_req = {
        "name": "CPU cores", 
        "value": system_info["hardware"]["cpu_count"], 
        "required": "2+", 
        "status": system_info["hardware"]["cpu_count"] >= 2
    }
    if not cpu_req["status"]:
        system_info["status"] = False
        system_info["message"] = "CPU does not meet requirements"
    requirements.append(cpu_req)
    
    # Check memory
    memory_req = {
        "name": "Memory (RAM)", 
        "value": f"{system_info['hardware']['memory_total_gb']} GB", 
        "required": "4+ GB", 
        "status": system_info["hardware"]["memory_total_gb"] >= 4
    }
    if not memory_req["status"]:
        system_info["status"] = False
        system_info["message"] = "Memory does not meet requirements"
    requirements.append(memory_req)
    
    # Check disk space
    disk_space_req = {
        "name": "Disk space", 
        "value": f"{system_info['storage']['disks'][0]['free_gb']} GB free", 
        "required": "10+ GB free", 
        "status": system_info["storage"]["disks"][0]["free_gb"] >= 10
    }
    if not disk_space_req["status"]:
        system_info["status"] = False
        system_info["message"] = "Disk space does not meet requirements"
    requirements.append(disk_space_req)
    
    system_info["requirements"] = requirements
    
    return system_info

def get_ip_address():
    """Get the IP address of the current machine"""
    try:
        # This creates a socket to a public server but doesn't send any data
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to determine IP address"

def get_network_interfaces():
    """Get information about network interfaces"""
    interfaces = []
    
    if_addrs = psutil.net_if_addrs()
    if_stats = psutil.net_if_stats()
    
    for interface_name, addr_list in if_addrs.items():
        if interface_name in if_stats:
            # Check if interface is up and running
            is_up = if_stats[interface_name].isup
            
            # Get IP addresses
            ipv4_addr = None
            ipv6_addr = None
            mac_addr = None
            
            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    ipv4_addr = addr.address
                elif addr.family == socket.AF_INET6:
                    ipv6_addr = addr.address
                elif addr.family == psutil.AF_LINK:
                    mac_addr = addr.address
            
            interfaces.append({
                "name": interface_name,
                "ip_address": ipv4_addr,
                "ipv6_address": ipv6_addr,
                "mac_address": mac_addr,
                "is_up": is_up
            })
    
    return interfaces

def get_disk_info():
    """Get information about disk drives"""
    disks = []
    
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent_used": usage.percent
            })
        except (PermissionError, FileNotFoundError):
            # Some mountpoints might not be accessible
            continue
    
    return disks

def check_vmm_prerequisites(check_windows=True):
    """
    Check if the system has the prerequisites for VMM implementation.
    Returns a dictionary with check results.
    """
    results = {
        "status": True,
        "checks": [],
        "errors": [],
        "warnings": []
    }
    
    # Check operating system
    os_check = {
        "name": "Operating System",
        "status": True,
        "message": "Check completed",
        "details": platform.system()
    }
    
    # Check if running on Windows if required
    if check_windows and platform.system() != "Windows":
        os_check["status"] = False
        os_check["message"] = f"Expected Windows, found {platform.system()}"
        results["errors"].append(f"VMM requires Windows Server, but current OS is {platform.system()}")
        results["status"] = False
    
    results["checks"].append(os_check)
    
    # Check admin privileges (simplified for cross-platform compatibility)
    admin_check = {
        "name": "Administrative Privileges",
        "status": True,
        "message": "Check completed",
        "details": "Not verified in this environment"
    }
    
    try:
        if platform.system() == "Windows":
            # On Windows, attempt to access admin-only directory
            admin_status = os.access("C:\\Windows\\System32\\config", os.R_OK)
            admin_check["details"] = "Administrative" if admin_status else "Standard user"
            if not admin_status:
                admin_check["status"] = False
                admin_check["message"] = "Administrative privileges required"
                results["warnings"].append("Tool is not running with administrative privileges")
    except:
        admin_check["status"] = False
        admin_check["message"] = "Unable to determine privilege level"
        results["warnings"].append("Could not verify administrative privileges")
    
    results["checks"].append(admin_check)
    
    # Check memory
    memory_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    memory_check = {
        "name": "Memory",
        "status": memory_gb >= 4,
        "message": f"{memory_gb} GB available",
        "details": f"Minimum recommended: 4 GB"
    }
    
    if not memory_check["status"]:
        results["warnings"].append(f"System has {memory_gb} GB RAM, VMM requires at least 4 GB")
        results["status"] = False
    
    results["checks"].append(memory_check)
    
    # Check CPU
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_check = {
        "name": "CPU",
        "status": cpu_cores >= 2,
        "message": f"{cpu_cores} physical cores available",
        "details": "Minimum recommended: 2 cores"
    }
    
    if not cpu_check["status"]:
        results["warnings"].append(f"System has {cpu_cores} CPU cores, VMM requires at least 2 cores")
        results["status"] = False
    
    results["checks"].append(cpu_check)
    
    # Check disk space
    disk_space_gb = 0
    try:
        disk_space_gb = round(psutil.disk_usage(os.getcwd()).free / (1024**3), 2)
    except:
        pass
    
    disk_check = {
        "name": "Disk Space",
        "status": disk_space_gb >= 10,
        "message": f"{disk_space_gb} GB free space available",
        "details": "Minimum recommended: 10 GB"
    }
    
    if not disk_check["status"]:
        results["warnings"].append(f"System has {disk_space_gb} GB free disk space, VMM requires at least 10 GB")
        results["status"] = False
    
    results["checks"].append(disk_check)
    
    # Check network connectivity
    network_check = {
        "name": "Network Connectivity",
        "status": True,
        "message": "Network is accessible",
        "details": "Network interfaces detected"
    }
    
    # Check if any network interface is up
    if_stats = psutil.net_if_stats()
    active_interfaces = [iface for iface, stats in if_stats.items() if stats.isup]
    
    if not active_interfaces:
        network_check["status"] = False
        network_check["message"] = "No active network interfaces detected"
        results["errors"].append("No active network connection found")
        results["status"] = False
    
    results["checks"].append(network_check)
    
    return results

def create_system_visualization(system_info):
    """
    Create a visual representation of the system information.
    Returns a dictionary with Plotly figures.
    """
    figures = {}
    
    # Create CPU usage gauge
    cpu_usage = psutil.cpu_percent()
    fig_cpu = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cpu_usage,
        title={"text": "CPU Usage"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "blue"},
            "steps": [
                {"range": [0, 50], "color": "lightgray"},
                {"range": [50, 80], "color": "gray"},
                {"range": [80, 100], "color": "red"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 90
            }
        }
    ))
    
    fig_cpu.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    figures["cpu"] = fig_cpu
    
    # Create memory usage gauge
    memory_percent = psutil.virtual_memory().percent
    fig_memory = go.Figure(go.Indicator(
        mode="gauge+number",
        value=memory_percent,
        title={"text": "Memory Usage"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "blue"},
            "steps": [
                {"range": [0, 50], "color": "lightgray"},
                {"range": [50, 80], "color": "gray"},
                {"range": [80, 100], "color": "red"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 90
            }
        }
    ))
    
    fig_memory.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    figures["memory"] = fig_memory
    
    # Create disk usage chart
    disk_data = []
    for disk in system_info["storage"]["disks"]:
        disk_data.append({
            "Disk": disk["mountpoint"],
            "Used (GB)": disk["used_gb"],
            "Free (GB)": disk["free_gb"]
        })
    
    df_disk = pd.DataFrame(disk_data)
    fig_disk = px.bar(df_disk, x="Disk", y=["Used (GB)", "Free (GB)"], title="Disk Usage",
                     barmode="stack", height=300)
    
    fig_disk.update_layout(
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    figures["disk"] = fig_disk
    
    # Create system requirements check
    req_status = [req["status"] for req in system_info["requirements"]]
    req_names = [req["name"] for req in system_info["requirements"]]
    req_colors = ["green" if status else "red" for status in req_status]
    
    fig_req = go.Figure(go.Bar(
        x=req_names,
        y=[1] * len(req_names),
        marker_color=req_colors,
        text=[req["value"] for req in system_info["requirements"]],
        textposition="auto"
    ))
    
    fig_req.update_layout(
        title="System Requirements",
        yaxis_visible=False,
        height=300,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    figures["requirements"] = fig_req
    
    return figures
