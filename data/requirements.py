def get_hardware_requirements():
    """
    Get hardware requirements for VMM cluster implementation.
    Returns a dictionary of hardware requirements.
    """
    hardware_requirements = {
        "server_requirements": [
            {
                "Component": "CPU",
                "Minimum": "4 cores",
                "Recommended": "8+ cores",
                "Notes": "3.0 GHz oder höher für optimale Leistung"
            },
            {
                "Component": "Memory (RAM)",
                "Minimum": "16 GB",
                "Recommended": "32+ GB",
                "Notes": "64+ GB für produktive Umgebungen empfohlen"
            },
            {
                "Component": "System Disk",
                "Minimum": "150 GB SSD",
                "Recommended": "300+ GB NVMe",
                "Notes": "RAID 1 für Betriebssystem empfohlen"
            },
            {
                "Component": "Network",
                "Minimum": "2 x 10 Gbps",
                "Recommended": "2x2 10 Gbps (Klassischer Storage) / 2x2 25 Gbps (Storage Spaces Direct)",
                "Notes": "Getrennte Netzwerke für Management, VM-Traffic, Live Migration und Storage"
            },
            {
                "Component": "Operating System",
                "Minimum": "Windows Server 2022",
                "Recommended": "Windows Server 2025",
                "Notes": "Datacenter Edition für unbegrenzte VMs empfohlen"
            }
        ],
        "storage_requirements": [
            {
                "Component": "Storage Type",
                "Minimum": "Shared Storage (SAN, iSCSI, FC)",
                "Recommended": "Storage Spaces Direct (S2D)",
                "Notes": "Hochverfügbare Speicherlösung erforderlich"
            },
            {
                "Component": "Storage Capacity",
                "Minimum": "1 TB verwendbar",
                "Recommended": "5+ TB je nach VM-Anzahl",
                "Notes": "Min. 30% Reserve für künftiges Wachstum einplanen"
            },
            {
                "Component": "Storage Performance",
                "Minimum": "All-Flash für Produktionsumgebungen",
                "Recommended": "NVMe + Tiering",
                "Notes": "Leistungsreserven für Lastspitzen berücksichtigen"
            },
            {
                "Component": "Storage Connectivity",
                "Minimum": "10 Gbps iSCSI oder 16 Gbps FC",
                "Recommended": "25+ Gbps iSCSI oder 32 Gbps FC",
                "Notes": "Redundante Pfade und MPIO zwingend erforderlich"
            }
        ],
        "network_requirements": [
            {
                "Component": "Management Network",
                "Minimum": "10 Gbps",
                "Recommended": "10 Gbps redundant",
                "Notes": "Für Host-Management und VM-Konfiguration"
            },
            {
                "Component": "Live Migration Network",
                "Minimum": "10 Gbps dediziert",
                "Recommended": "25+ Gbps dediziert",
                "Notes": "Separates Netzwerk für VM-Migrationen erforderlich"
            },
            {
                "Component": "VM Network",
                "Minimum": "10 Gbps redundant",
                "Recommended": "25+ Gbps redundant",
                "Notes": "Für VM-Konnektivität mit externen Netzwerken"
            },
            {
                "Component": "Cluster Network",
                "Minimum": "10 Gbps",
                "Recommended": "10 Gbps redundant",
                "Notes": "Für Cluster-Heartbeat und CSV-Kommunikation"
            },
            {
                "Component": "Storage Network",
                "Minimum": "10 Gbps dediziert redundant",
                "Recommended": "25 Gbps dediziert (50 Gbps für S2D)",
                "Notes": "Dediziertes Netzwerk für Storage-Traffic erforderlich"
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
