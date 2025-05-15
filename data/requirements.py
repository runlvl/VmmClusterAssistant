def get_hardware_requirements():
    """
    Get hardware requirements for VMM cluster implementation.
    Returns a dictionary of hardware requirements.
    """
    hardware_requirements = {
        "server_requirements": [
            {
                "Component": "CPU",
                "Minimum": "2 cores",
                "Recommended": "4+ cores",
                "Notes": "2.0 GHz or faster"
            },
            {
                "Component": "Memory (RAM)",
                "Minimum": "8 GB",
                "Recommended": "16+ GB",
                "Notes": "Additional memory for VMs"
            },
            {
                "Component": "System Disk",
                "Minimum": "100 GB",
                "Recommended": "200+ GB",
                "Notes": "SSD recommended"
            },
            {
                "Component": "Network",
                "Minimum": "2 x 10 Gbps",
                "Recommended": "2x2 10 Gbps (Classical Storage) / 2x2 25 Gbps (Storage Spaces Direct)",
                "Notes": "Separate networks for management, VM traffic, and storage"
            },
            {
                "Component": "Operating System",
                "Minimum": "Windows Server 2022",
                "Recommended": "Windows Server 2025",
                "Notes": "Standard or Datacenter edition"
            }
        ],
        "storage_requirements": [
            {
                "Component": "Storage Type",
                "Minimum": "Local Storage",
                "Recommended": "SAN, iSCSI, FC",
                "Notes": "Shared storage recommended"
            },
            {
                "Component": "Storage Capacity",
                "Minimum": "500 GB",
                "Recommended": "As needed for VMs",
                "Notes": "Plan for VM storage and growth"
            },
            {
                "Component": "Storage Connectivity",
                "Minimum": "1 Gbps",
                "Recommended": "10+ Gbps",
                "Notes": "Redundant connections recommended"
            },
            {
                "Component": "MPIO",
                "Minimum": "Recommended",
                "Recommended": "Required for HA",
                "Notes": "For redundant storage connectivity"
            }
        ],
        "network_requirements": [
            {
                "Component": "Management Network",
                "Minimum": "10 Gbps",
                "Recommended": "10 Gbps",
                "Notes": "For host management"
            },
            {
                "Component": "Live Migration Network",
                "Minimum": "10 Gbps",
                "Recommended": "25 Gbps",
                "Notes": "Optional if multiple clusters or standalone hosts exist"
            },
            {
                "Component": "VM Network",
                "Minimum": "10 Gbps",
                "Recommended": "25 Gbps",
                "Notes": "For VM traffic"
            },
            {
                "Component": "Cluster Network",
                "Minimum": "10 Gbps",
                "Recommended": "10 Gbps",
                "Notes": "For cluster heartbeat"
            }
        ]
    }
    
    return hardware_requirements

def get_software_requirements():
    """
    Get software requirements for VMM cluster implementation.
    Returns a dictionary of software requirements.
    """
    software_requirements = {
        "os_requirements": [
            {
                "Component": "Windows Server 2025",
                "Editions": "Standard or Datacenter",
                "Notes": "Latest updates recommended"
            },
            {
                "Component": "Windows Server 2022",
                "Editions": "Standard or Datacenter",
                "Notes": "Latest updates recommended"
            }
        ],
        "required_features": [
            {
                "Feature": "Hyper-V",
                "Required": "Yes",
                "Notes": "Core virtualization role"
            },
            {
                "Feature": "Failover Clustering",
                "Required": "Yes",
                "Notes": "Required for high availability"
            },
            {
                "Feature": "Multipath I/O",
                "Required": "Yes",
                "Notes": "For redundant storage connectivity"
            },
            {
                "Feature": "Data Deduplication",
                "Required": "Optional",
                "Notes": "For storage efficiency"
            }
        ],
        "vmm_requirements": [
            {
                "Component": "System Center 2022/2025",
                "Compatible OS": "Windows Server 2022/2025",
                "Notes": "Latest version recommended (Optional)"
            }
        ],
        "sql_requirements": [
            {
                "Component": "SQL Server 2022",
                "Compatible OS": "Windows Server 2022/2025",
                "Notes": "Latest version recommended"
            }
        ],
        "file_system_requirements": [
            {
                "Component": "NTFS",
                "Usage": "System volumes, non-clustered storage",
                "Notes": "Default file system for Windows"
            },
            {
                "Component": "ReFS",
                "Usage": "Storage Spaces Direct only",
                "Notes": "Do NOT use with classical storage"
            },
            {
                "Component": "CSV Configuration",
                "Usage": "At least one CSV per host",
                "Notes": "Required for proper failover functionality"
            }
        ]
    }
    
    return software_requirements
