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
                "Minimum": "2 x 1 Gbps",
                "Recommended": "4+ NICs (10 Gbps)",
                "Notes": "Separate networks recommended"
            },
            {
                "Component": "Operating System",
                "Minimum": "Windows Server 2019",
                "Recommended": "Windows Server 2022",
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
                "Minimum": "1 Gbps",
                "Recommended": "10 Gbps",
                "Notes": "For host and VMM management"
            },
            {
                "Component": "Live Migration Network",
                "Minimum": "1 Gbps",
                "Recommended": "10+ Gbps",
                "Notes": "Dedicated network recommended"
            },
            {
                "Component": "VM Network",
                "Minimum": "1 Gbps",
                "Recommended": "10+ Gbps",
                "Notes": "For VM traffic"
            },
            {
                "Component": "Cluster Network",
                "Minimum": "1 Gbps",
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
                "Component": "Windows Server 2022",
                "Editions": "Standard or Datacenter",
                "Notes": "Latest updates recommended"
            },
            {
                "Component": "Windows Server 2019",
                "Editions": "Standard or Datacenter",
                "Notes": "Latest updates recommended"
            },
            {
                "Component": "Windows Server 2016",
                "Editions": "Standard or Datacenter",
                "Notes": "Consider upgrading to newer version"
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
                "Component": "System Center 2022",
                "Compatible OS": "Windows Server 2022/2019",
                "Notes": "Latest version recommended"
            },
            {
                "Component": "System Center 2019",
                "Compatible OS": "Windows Server 2019/2016",
                "Notes": "Compatible with Windows Server 2019"
            },
            {
                "Component": "System Center 2016",
                "Compatible OS": "Windows Server 2016",
                "Notes": "Consider upgrading to newer version"
            }
        ],
        "sql_requirements": [
            {
                "Component": "SQL Server 2022",
                "Compatible OS": "Windows Server 2022/2019",
                "Notes": "Latest version recommended"
            },
            {
                "Component": "SQL Server 2019",
                "Compatible OS": "Windows Server 2019/2016",
                "Notes": "Compatible with Windows Server 2019"
            },
            {
                "Component": "SQL Server 2017",
                "Compatible OS": "Windows Server 2019/2016",
                "Notes": "Supported version"
            },
            {
                "Component": "SQL Server 2016",
                "Compatible OS": "Windows Server 2016",
                "Notes": "Consider upgrading to newer version"
            }
        ]
    }
    
    return software_requirements
