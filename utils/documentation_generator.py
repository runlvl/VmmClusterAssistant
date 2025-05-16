import os
import jinja2
import datetime
import yaml
import pandas as pd
import plotly.io as pio
import base64
from io import BytesIO

def generate_implementation_documentation(config):
    """
    Generate comprehensive documentation based on the VMM cluster configuration.
    
    Args:
        config: Dictionary containing the complete cluster configuration
        
    Returns:
        HTML string with the formatted documentation
    """
    # Get logo for branding
    logo_path = "assets/bechtle_logo.png"
    with open(logo_path, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create Jinja2 environment
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    
    # Create template string inline since we don't have external files
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VMM Cluster Implementation Documentation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            h1 {
                color: #1C5631; /* Bechtle Grün */
                border-bottom: 2px solid #1C5631;
                padding-bottom: 10px;
            }
            h2 {
                color: #1C5631; /* Bechtle Grün */
                margin-top: 25px;
            }
            h3 {
                color: #1C5631; /* Bechtle Grün */
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            th {
                background-color: #1C5631; /* Bechtle Grün */
                color: white;
                text-align: left;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .image-container {
                text-align: center;
                margin: 20px 0;
            }
            .image-container img {
                max-width: 100%;
                height: auto;
            }
            .warning {
                background-color: #fff3cd;
                color: #856404;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
                border-left: 4px solid #ffc107;
            }
            .info {
                background-color: #e8f4f8;
                color: #1C5631; /* Bechtle Grün */
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
                border-left: 4px solid #1C5631; /* Bechtle Grün */
            }
            .success {
                background-color: #e6f3eb;
                color: #1C5631; /* Bechtle Grün */
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
                border-left: 4px solid #1C5631; /* Bechtle Grün */
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
                border-left: 4px solid #dc3545;
            }
            .footer {
                margin-top: 40px;
                border-top: 1px solid #ddd;
                padding-top: 10px;
                font-size: 0.8em;
                color: #777;
            }
            .page-break {
                page-break-after: always;
            }
            @media print {
                body {
                    padding: 10px;
                }
                .no-print {
                    display: none;
                }
            }
        </style>
    </head>
    <body>
        <div style="display: flex; align-items: flex-end; padding-bottom: 1rem; margin-top: 0.5rem;">
            <div style="margin-right: 12px; line-height: 0;">
                <img src="data:image/png;base64,{{ logo_base64 }}" style="height: 50px; display: block;">
            </div>
            <div style="display: inline-block; line-height: 1; padding-bottom: 4px;">
                <div style="color: #1C5631; font-size: 22px; font-weight: 600; margin: 0; white-space: nowrap; padding-left: 5px;">
                    <span style="font-size: 30px; font-weight: 700;">Professional Services</span> | Datacenter & Endpoint
                </div>
            </div>
        </div>
        
        <h1>VMM Cluster Implementation Documentation</h1>
        <p>
            <strong>Generated:</strong> {{ generation_date }}<br>
            <strong>Organization:</strong> {{ config.organization|default('Not specified') }}<br>
            <strong>Project:</strong> {{ config.project_name|default('VMM Cluster Implementation') }}
        </p>
        
        <div class="info">
            This document provides comprehensive documentation for the implementation of a System Center Virtual Machine Manager (VMM) cluster.
            It includes hardware and software specifications, network and storage configurations, security settings, and implementation guidelines.
        </div>
        
        <h2>Table of Contents</h2>
        <ol>
            <li><a href="#overview">Implementation Overview</a></li>
            <li><a href="#hardware">Hardware Configuration</a></li>
            <li><a href="#software">Software Configuration</a></li>
            <li><a href="#network">Network Configuration</a></li>
            <li><a href="#storage">Storage Configuration</a></li>
            <li><a href="#security">Security Settings</a></li>
            <li><a href="#ha">High Availability Configuration</a></li>
            <li><a href="#backup">Backup and Restore</a></li>
            <li><a href="#roles">Roles and Permissions</a></li>
            <li><a href="#monitoring">Monitoring</a></li>
            <li><a href="#implementation">Implementation Checklist</a></li>
        </ol>
        
        <div class="page-break"></div>
        
        <h2 id="overview">1. Implementation Overview</h2>
        <p>
            This document outlines the implementation plan for a VMM cluster consisting of 
            {{ config.hardware.host_count|default(2) }} Hyper-V hosts using 
            {{ config.storage.storage_type|default('shared storage') }}.
            The VMM server will be configured in {{ "high availability mode" if config.ha.enabled else "standalone mode" }}.
        </p>
        
        <h3>Architecture Overview</h3>
        {% if config.architecture_diagram %}
        <div class="image-container">
            <img src="data:image/png;base64,{{ config.architecture_diagram }}" alt="Architecture Diagram">
        </div>
        {% endif %}
        
        <h3>Implementation Timeline</h3>
        <table>
            <thead>
                <tr>
                    <th>Phase</th>
                    <th>Description</th>
                    <th>Estimated Duration</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1. Prerequisites</td>
                    <td>Verify hardware and software requirements</td>
                    <td>1 day</td>
                </tr>
                <tr>
                    <td>2. Infrastructure</td>
                    <td>Configure hardware, networking, and storage</td>
                    <td>2-3 days</td>
                </tr>
                <tr>
                    <td>3. Installation</td>
                    <td>Install and configure VMM</td>
                    <td>1-2 days</td>
                </tr>
                <tr>
                    <td>4. High Availability</td>
                    <td>Configure clustering and high availability</td>
                    <td>1 day</td>
                </tr>
                <tr>
                    <td>5. Testing</td>
                    <td>Validate functionality and failover</td>
                    <td>1-2 days</td>
                </tr>
                <tr>
                    <td>6. Documentation</td>
                    <td>Finalize documentation and handover</td>
                    <td>1 day</td>
                </tr>
            </tbody>
        </table>
        
        <div class="page-break"></div>
        
        <h2 id="hardware">2. Hardware Configuration</h2>
        
        <h3>Server Specifications</h3>
        {% if config.hardware and config.hardware.servers %}
        <table>
            <thead>
                <tr>
                    <th>Server Role</th>
                    <th>Model</th>
                    <th>CPU</th>
                    <th>Memory</th>
                    <th>Storage</th>
                    <th>Network</th>
                </tr>
            </thead>
            <tbody>
                {% for server in config.hardware.servers %}
                <tr>
                    <td>{{ server.role }}</td>
                    <td>{{ server.model|default('Not specified') }}</td>
                    <td>{{ server.cpu|default('Not specified') }}</td>
                    <td>{{ server.memory|default('Not specified') }}</td>
                    <td>{{ server.storage|default('Not specified') }}</td>
                    <td>{{ server.network|default('Not specified') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No server specifications have been defined.</p>
        {% endif %}
        
        <h3>Hardware Requirements Verification</h3>
        <ul>
            {% if config.hardware.requirements_met %}
                <li class="success">All hardware requirements have been verified and met.</li>
            {% else %}
                <li class="warning">Hardware requirements verification is pending.</li>
            {% endif %}
            
            {% if config.hardware.homogeneous %}
                <li class="success">Servers are homogeneous as recommended.</li>
            {% else %}
                <li class="warning">Servers are not homogeneous. This may cause performance inconsistencies.</li>
            {% endif %}
        </ul>
        
        <h3>Hardware Best Practices</h3>
        <ul>
            <li>Use homogeneous hardware for all cluster nodes</li>
            <li>Ensure all hardware is on the Windows Server Catalog</li>
            <li>Provide sufficient resources for the expected VM workload</li>
            <li>Configure hardware-level redundancy (power supplies, network adapters, etc.)</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="software">3. Software Configuration</h2>
        
        <h3>Operating System</h3>
        <p>
            {{ config.software.os|default('Windows Server 2019/2022') }} will be installed on all servers.
            The operating system will be configured with the minimal installation option to reduce the attack surface.
        </p>
        
        <h3>Required Software Components</h3>
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Version</th>
                    <th>Purpose</th>
                    <th>Installation Location</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Windows Server</td>
                    <td>{{ config.software.os_version|default('2019/2022') }}</td>
                    <td>Base operating system</td>
                    <td>All servers</td>
                </tr>
                <tr>
                    <td>System Center VMM</td>
                    <td>{{ config.software.vmm_version|default('Latest') }}</td>
                    <td>Virtual machine management</td>
                    <td>VMM servers</td>
                </tr>
                <tr>
                    <td>SQL Server</td>
                    <td>{{ config.software.sql_version|default('Latest') }}</td>
                    <td>VMM database</td>
                    <td>Database servers</td>
                </tr>
                <tr>
                    <td>Windows ADK</td>
                    <td>{{ config.software.adk_version|default('Latest') }}</td>
                    <td>Deployment tools</td>
                    <td>VMM servers</td>
                </tr>
                <tr>
                    <td>Failover Clustering</td>
                    <td>{{ config.software.os_version|default('2019/2022') }}</td>
                    <td>High availability</td>
                    <td>All cluster nodes</td>
                </tr>
                <tr>
                    <td>Multipath I/O</td>
                    <td>{{ config.software.os_version|default('2019/2022') }}</td>
                    <td>Storage connectivity</td>
                    <td>All Hyper-V hosts</td>
                </tr>
            </tbody>
        </table>
        
        <h3>Software Best Practices</h3>
        <ul>
            <li>Keep all software components updated with the latest security patches</li>
            <li>Install only necessary roles and features</li>
            <li>Do not install VMM on the Hyper-V host partition</li>
            <li>Use consistent software versions across all servers</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="network">4. Network Configuration</h2>
        
        <h3>Network Architecture</h3>
        {% if config.network_diagram %}
        <div class="image-container">
            <img src="data:image/png;base64,{{ config.network_diagram }}" alt="Network Diagram">
        </div>
        {% endif %}
        
        <h3>Network Configuration Details</h3>
        <table>
            <thead>
                <tr>
                    <th>Network Type</th>
                    <th>VLAN</th>
                    <th>IP Range</th>
                    <th>Subnet Mask</th>
                    <th>Gateway</th>
                    <th>Purpose</th>
                </tr>
            </thead>
            <tbody>
                {% if config.network and config.network.management_network %}
                <tr>
                    <td>Management</td>
                    <td>{{ config.network.management_network.vlan|default('N/A') }}</td>
                    <td>{{ config.network.management_network.ip_range|default('N/A') }}</td>
                    <td>{{ config.network.management_network.subnet|default('N/A') }}</td>
                    <td>{{ config.network.management_network.gateway|default('N/A') }}</td>
                    <td>Host and VMM management</td>
                </tr>
                {% endif %}
                
                {% if config.network and config.network.migration_network %}
                <tr>
                    <td>Live Migration</td>
                    <td>{{ config.network.migration_network.vlan|default('N/A') }}</td>
                    <td>{{ config.network.migration_network.ip_range|default('N/A') }}</td>
                    <td>{{ config.network.migration_network.subnet|default('N/A') }}</td>
                    <td>{{ config.network.migration_network.gateway|default('N/A') }}</td>
                    <td>VM live migration traffic</td>
                </tr>
                {% endif %}
                
                {% if config.network and config.network.vm_network %}
                <tr>
                    <td>VM Network</td>
                    <td>{{ config.network.vm_network.vlan|default('N/A') }}</td>
                    <td>{{ config.network.vm_network.ip_range|default('N/A') }}</td>
                    <td>{{ config.network.vm_network.subnet|default('N/A') }}</td>
                    <td>{{ config.network.vm_network.gateway|default('N/A') }}</td>
                    <td>Virtual machine traffic</td>
                </tr>
                {% endif %}
                
                {% if config.network and config.network.cluster_network %}
                <tr>
                    <td>Cluster</td>
                    <td>{{ config.network.cluster_network.vlan|default('N/A') }}</td>
                    <td>{{ config.network.cluster_network.ip_range|default('N/A') }}</td>
                    <td>{{ config.network.cluster_network.subnet|default('N/A') }}</td>
                    <td>{{ config.network.cluster_network.gateway|default('N/A') }}</td>
                    <td>Cluster communication</td>
                </tr>
                {% endif %}
            </tbody>
        </table>
        
        <h3>Network Adapter Configuration</h3>
        <table>
            <thead>
                <tr>
                    <th>Server</th>
                    <th>Adapter Name</th>
                    <th>Network Type</th>
                    <th>Speed</th>
                    <th>Teaming</th>
                </tr>
            </thead>
            <tbody>
                {% if config.network and config.network.adapters %}
                {% for adapter in config.network.adapters %}
                <tr>
                    <td>{{ adapter.server }}</td>
                    <td>{{ adapter.name }}</td>
                    <td>{{ adapter.network_type }}</td>
                    <td>{{ adapter.speed }}</td>
                    <td>{{ "Yes" if adapter.teaming else "No" }}</td>
                </tr>
                {% endfor %}
                {% else %}
                <tr>
                    <td colspan="5">No adapter configuration defined.</td>
                </tr>
                {% endif %}
            </tbody>
        </table>
        
        <h3>Network Best Practices</h3>
        <ul>
            <li>Use separate networks for different traffic types (management, live migration, VM)</li>
            <li>Configure NIC teaming for redundancy where appropriate</li>
            <li>Enable IPsec on the live migration network for security</li>
            <li>Use consistent network naming conventions across all hosts</li>
            <li>Configure QoS policies only if needed based on observed performance</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="storage">5. Storage Configuration</h2>
        
        <h3>Storage Architecture</h3>
        {% if config.storage_diagram %}
        <div class="image-container">
            <img src="data:image/png;base64,{{ config.storage_diagram }}" alt="Storage Diagram">
        </div>
        {% endif %}
        
        <h3>Storage Configuration Details</h3>
        <table>
            <thead>
                <tr>
                    <th>Storage Type</th>
                    <th>Purpose</th>
                    <th>Size</th>
                    <th>Format</th>
                    <th>Redundancy</th>
                </tr>
            </thead>
            <tbody>
                {% if config.storage and config.storage.quorum_disk %}
                <tr>
                    <td>Quorum Disk</td>
                    <td>Cluster quorum witness</td>
                    <td>{{ config.storage.quorum_disk.size_gb|default('1') }} GB</td>
                    <td>{{ config.storage.quorum_disk.format|default('NTFS') }}</td>
                    <td>{{ config.storage.quorum_disk.redundancy|default('N/A') }}</td>
                </tr>
                {% endif %}
                
                {% if config.storage and config.storage.csv_volumes %}
                {% for volume in config.storage.csv_volumes %}
                <tr>
                    <td>CSV Volume {{ loop.index }}</td>
                    <td>{{ volume.purpose|default('VM Storage') }}</td>
                    <td>{{ volume.size_gb|default('N/A') }} GB</td>
                    <td>{{ volume.format|default('NTFS') }}</td>
                    <td>{{ volume.redundancy|default('N/A') }}</td>
                </tr>
                {% endfor %}
                {% endif %}
            </tbody>
        </table>
        
        <h3>Storage Best Practices</h3>
        <ul>
            <li>Use shared storage for all cluster nodes</li>
            <li>Implement MPIO for redundant storage connectivity</li>
            <li>Use small (1-5 GB) LUN for quorum disk</li>
            <li>Do not share storage between different clusters</li>
            <li>Consider using multiple CSV volumes for better performance and management</li>
            <li>Place only highly available VMs on cluster shared volumes</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="security">6. Security Settings</h2>
        
        <h3>Security Configuration</h3>
        <table>
            <thead>
                <tr>
                    <th>Security Aspect</th>
                    <th>Configuration</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Host OS Hardening</td>
                    <td>{{ "Enabled" if config.security and config.security.host_hardening else "Not configured" }}</td>
                    <td>Minimal Windows Server installation, latest security updates</td>
                </tr>
                <tr>
                    <td>Network Isolation</td>
                    <td>{{ "Enabled" if config.security and config.security.network_isolation else "Not configured" }}</td>
                    <td>Separate networks for different traffic types</td>
                </tr>
                <tr>
                    <td>IPsec for Migration</td>
                    <td>{{ "Enabled" if config.security and config.security.ipsec_migration else "Not configured" }}</td>
                    <td>Encryption for live migration traffic</td>
                </tr>
                <tr>
                    <td>SMB Encryption</td>
                    <td>{{ "Enabled" if config.security and config.security.smb_encryption else "Not configured" }}</td>
                    <td>End-to-end encryption for SMB data</td>
                </tr>
                <tr>
                    <td>Distributed Key Management</td>
                    <td>{{ "Enabled" if config.security and config.security.dkm else "Not configured" }}</td>
                    <td>Secure storage of encryption keys in Active Directory</td>
                </tr>
                <tr>
                    <td>Code Integrity Policies</td>
                    <td>{{ "Enabled" if config.security and config.security.code_integrity else "Not configured" }}</td>
                    <td>Prevent unauthorized code execution</td>
                </tr>
            </tbody>
        </table>
        
        <h3>Role-Based Access Control</h3>
        <table>
            <thead>
                <tr>
                    <th>Role</th>
                    <th>Permissions</th>
                    <th>Assigned To</th>
                </tr>
            </thead>
            <tbody>
                {% if config.security and config.security.roles %}
                {% for role in config.security.roles %}
                <tr>
                    <td>{{ role.name }}</td>
                    <td>{{ role.permissions|default('Not specified') }}</td>
                    <td>{{ role.assigned_to|default('Not assigned') }}</td>
                </tr>
                {% endfor %}
                {% else %}
                <tr>
                    <td colspan="3">No roles defined.</td>
                </tr>
                {% endif %}
            </tbody>
        </table>
        
        <h3>Security Best Practices</h3>
        <ul>
            <li>Use the principle of least privilege for all accounts</li>
            <li>Implement role-based access control</li>
            <li>Keep all systems updated with security patches</li>
            <li>Use encrypted communications for sensitive traffic</li>
            <li>Implement secure boot and code integrity where possible</li>
            <li>Regularly audit and review access permissions</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="ha">7. High Availability Configuration</h2>
        
        <h3>High Availability Architecture</h3>
        {% if config.ha and config.ha.diagram %}
        <div class="image-container">
            <img src="data:image/png;base64,{{ config.ha.diagram }}" alt="High Availability Diagram">
        </div>
        {% endif %}
        
        <h3>Failover Cluster Configuration</h3>
        <table>
            <thead>
                <tr>
                    <th>Cluster Name</th>
                    <th>Node Count</th>
                    <th>Quorum Type</th>
                    <th>Witness Type</th>
                </tr>
            </thead>
            <tbody>
                {% if config.ha and config.ha.cluster %}
                <tr>
                    <td>{{ config.ha.cluster.name|default('VMM-Cluster') }}</td>
                    <td>{{ config.ha.cluster.node_count|default(2) }}</td>
                    <td>{{ config.ha.cluster.quorum_type|default('Node Majority with Disk Witness') }}</td>
                    <td>{{ config.ha.cluster.witness_type|default('Disk Witness') }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="4">No cluster configuration defined.</td>
                </tr>
                {% endif %}
            </tbody>
        </table>
        
        <h3>VMM High Availability</h3>
        <ul>
            {% if config.ha and config.ha.enabled %}
                <li class="success">VMM will be deployed in high availability mode</li>
                <li>VMM service account: {{ config.ha.service_account|default('Not specified') }}</li>
                <li>Distributed Key Management configured in Active Directory</li>
                <li>VMM database will be hosted on a separate SQL cluster</li>
            {% else %}
                <li class="warning">VMM will be deployed in standalone mode (not highly available)</li>
            {% endif %}
        </ul>
        
        <h3>VMM Library High Availability</h3>
        <ul>
            {% if config.ha and config.ha.library_ha %}
                <li class="success">VMM library will be configured for high availability</li>
                <li>Library will be hosted on a clustered file server</li>
                <li>Library shares will be continuously available</li>
            {% else %}
                <li class="warning">VMM library will not be highly available</li>
            {% endif %}
        </ul>
        
        <h3>High Availability Best Practices</h3>
        <ul>
            <li>Test planned and unplanned failover scenarios regularly</li>
            <li>Ensure the cluster validation test passes before implementing</li>
            <li>Configure proper quorum settings to prevent split-brain scenarios</li>
            <li>Document failover procedures for administrators</li>
            <li>Implement monitoring for cluster health</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="backup">8. Backup and Restore</h2>
        
        <h3>Backup Strategy</h3>
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Backup Method</th>
                    <th>Frequency</th>
                    <th>Retention</th>
                </tr>
            </thead>
            <tbody>
                {% if config.backup %}
                <tr>
                    <td>VMM Database</td>
                    <td>{{ config.backup.vmm_db_method|default('SQL Backup') }}</td>
                    <td>{{ config.backup.vmm_db_frequency|default('Daily') }}</td>
                    <td>{{ config.backup.vmm_db_retention|default('30 days') }}</td>
                </tr>
                <tr>
                    <td>VMM Library</td>
                    <td>{{ config.backup.library_method|default('File Backup') }}</td>
                    <td>{{ config.backup.library_frequency|default('Weekly') }}</td>
                    <td>{{ config.backup.library_retention|default('30 days') }}</td>
                </tr>
                <tr>
                    <td>Virtual Machines</td>
                    <td>{{ config.backup.vm_method|default('Hyper-V Backup') }}</td>
                    <td>{{ config.backup.vm_frequency|default('Daily') }}</td>
                    <td>{{ config.backup.vm_retention|default('30 days') }}</td>
                </tr>
                <tr>
                    <td>Host Configuration</td>
                    <td>{{ config.backup.host_method|default('System State Backup') }}</td>
                    <td>{{ config.backup.host_frequency|default('Weekly') }}</td>
                    <td>{{ config.backup.host_retention|default('30 days') }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="4">No backup configuration defined.</td>
                </tr>
                {% endif %}
            </tbody>
        </table>
        
        <h3>Recovery Procedures</h3>
        <ul>
            <li><strong>VMM Server Recovery:</strong> Using SCVMMRecover.exe tool with backup database</li>
            <li><strong>Host Recovery:</strong> Reinstall host OS and add to VMM management</li>
            <li><strong>VM Recovery:</strong> Restore from backup or recreate from templates</li>
            <li><strong>Cluster Recovery:</strong> Rebuild cluster from surviving nodes or from scratch</li>
        </ul>
        
        <h3>Backup and Recovery Best Practices</h3>
        <ul>
            <li>Regularly test recovery procedures to ensure backups are valid</li>
            <li>Store backup media in a secure, off-site location</li>
            <li>Maintain documentation of recovery procedures</li>
            <li>Automate backup processes where possible</li>
            <li>Encrypt backup data for sensitive information</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="roles">9. Roles and Permissions</h2>
        
        <h3>Role-Based Access Control</h3>
        <table>
            <thead>
                <tr>
                    <th>Role</th>
                    <th>Description</th>
                    <th>Permissions</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Administrator</td>
                    <td>Full control over VMM environment</td>
                    <td>All permissions</td>
                </tr>
                <tr>
                    <td>Fabric Administrator</td>
                    <td>Manages physical infrastructure</td>
                    <td>Host, network, and storage management</td>
                </tr>
                <tr>
                    <td>VM Administrator</td>
                    <td>Manages virtual machines</td>
                    <td>Create, modify, and delete VMs</td>
                </tr>
                <tr>
                    <td>Read-Only Administrator</td>
                    <td>Views but cannot modify environment</td>
                    <td>View-only access to all components</td>
                </tr>
                <tr>
                    <td>Tenant Administrator</td>
                    <td>Manages tenant resources</td>
                    <td>Manage assigned tenant resources</td>
                </tr>
                {% if config.roles and config.roles.custom_roles %}
                {% for role in config.roles.custom_roles %}
                <tr>
                    <td>{{ role.name }}</td>
                    <td>{{ role.description|default('Custom role') }}</td>
                    <td>{{ role.permissions|default('Custom permissions') }}</td>
                </tr>
                {% endfor %}
                {% endif %}
            </tbody>
        </table>
        
        <h3>Service Accounts</h3>
        <table>
            <thead>
                <tr>
                    <th>Account</th>
                    <th>Purpose</th>
                    <th>Required Permissions</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>VMM Service Account</td>
                    <td>Runs the VMM service</td>
                    <td>Local administrator on VMM servers, SQL Server permissions</td>
                </tr>
                <tr>
                    <td>Run As Account</td>
                    <td>Performs operations on hosts and VMs</td>
                    <td>Local administrator on managed hosts</td>
                </tr>
                {% if config.roles and config.roles.service_accounts %}
                {% for account in config.roles.service_accounts %}
                <tr>
                    <td>{{ account.name }}</td>
                    <td>{{ account.purpose|default('Not specified') }}</td>
                    <td>{{ account.permissions|default('Not specified') }}</td>
                </tr>
                {% endfor %}
                {% endif %}
            </tbody>
        </table>
        
        <h3>User Management Best Practices</h3>
        <ul>
            <li>Implement role-based access control for all users</li>
            <li>Follow the principle of least privilege</li>
            <li>Regularly review and audit user access</li>
            <li>Use dedicated service accounts for automated processes</li>
            <li>Document all custom roles and their purposes</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="monitoring">10. Monitoring</h2>
        
        <h3>Monitoring Configuration</h3>
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Monitoring Method</th>
                    <th>Alert Thresholds</th>
                </tr>
            </thead>
            <tbody>
                {% if config.monitoring %}
                <tr>
                    <td>VMM Service</td>
                    <td>{{ config.monitoring.vmm_method|default('System Center Operations Manager') }}</td>
                    <td>Service status, resource usage</td>
                </tr>
                <tr>
                    <td>Failover Cluster</td>
                    <td>{{ config.monitoring.cluster_method|default('System Center Operations Manager') }}</td>
                    <td>Cluster health, node status, resource status</td>
                </tr>
                <tr>
                    <td>Hyper-V Hosts</td>
                    <td>{{ config.monitoring.host_method|default('System Center Operations Manager') }}</td>
                    <td>CPU > 80%, Memory > 90%, Disk space < 10%</td>
                </tr>
                <tr>
                    <td>Storage</td>
                    <td>{{ config.monitoring.storage_method|default('System Center Operations Manager') }}</td>
                    <td>Disk space < 20%, IO latency > 20ms</td>
                </tr>
                <tr>
                    <td>Network</td>
                    <td>{{ config.monitoring.network_method|default('System Center Operations Manager') }}</td>
                    <td>Bandwidth > 80%, packet loss > 0.1%</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="3">No monitoring configuration defined.</td>
                </tr>
                {% endif %}
            </tbody>
        </table>
        
        <h3>Notification Configuration</h3>
        <ul>
            {% if config.monitoring and config.monitoring.notifications %}
                <li>Email notifications: {{ "Enabled" if config.monitoring.notifications.email else "Disabled" }}</li>
                <li>SMS notifications: {{ "Enabled" if config.monitoring.notifications.sms else "Disabled" }}</li>
                <li>SNMP traps: {{ "Enabled" if config.monitoring.notifications.snmp else "Disabled" }}</li>
                <li>Recipients: {{ config.monitoring.notifications.recipients|default('Not specified') }}</li>
            {% else %}
                <li class="warning">No notification configuration defined.</li>
            {% endif %}
        </ul>
        
        <h3>Monitoring Best Practices</h3>
        <ul>
            <li>Establish baseline performance metrics</li>
            <li>Configure appropriate alert thresholds</li>
            <li>Set up automated responses for common issues</li>
            <li>Implement a tiered alert notification system</li>
            <li>Regularly review and tune monitoring settings</li>
            <li>Document troubleshooting procedures for common alerts</li>
        </ul>
        
        <div class="page-break"></div>
        
        <h2 id="implementation">11. Implementation Checklist</h2>
        
        <h3>Pre-Implementation Tasks</h3>
        <table>
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Status</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Verify hardware requirements</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.hardware_verified else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Verify software requirements</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.software_verified else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Prepare Active Directory</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.ad_prepared else "Pending" }}</td>
                    <td>Create service accounts and groups</td>
                </tr>
                <tr>
                    <td>Configure network infrastructure</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.network_configured else "Pending" }}</td>
                    <td>VLANs, routing, firewalls</td>
                </tr>
                <tr>
                    <td>Configure storage infrastructure</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.storage_configured else "Pending" }}</td>
                    <td>SAN zoning, LUN allocation</td>
                </tr>
            </tbody>
        </table>
        
        <h3>Installation Tasks</h3>
        <table>
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Status</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Install and configure operating system</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.os_installed else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Install required Windows features</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.features_installed else "Pending" }}</td>
                    <td>Hyper-V, Failover Clustering, MPIO</td>
                </tr>
                <tr>
                    <td>Configure failover cluster</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.cluster_configured else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Install SQL Server</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.sql_installed else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Install VMM</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.vmm_installed else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Configure high availability for VMM</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.vmm_ha_configured else "Pending" }}</td>
                    <td></td>
                </tr>
            </tbody>
        </table>
        
        <h3>Post-Implementation Tasks</h3>
        <table>
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Status</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Configure backup</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.backup_configured else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Configure monitoring</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.monitoring_configured else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Test failover scenarios</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.failover_tested else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Document configuration</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.documentation_completed else "Pending" }}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Training</td>
                    <td>{{ "Completed" if config.implementation and config.implementation.training_completed else "Pending" }}</td>
                    <td></td>
                </tr>
            </tbody>
        </table>
        
        <div class="footer">
            <p style="color: #1C5631; font-weight: bold;">
                © 2025 Bechtle Austria GmbH - <span style="font-size: 1.1em;">Professional Services</span> | Datacenter & Endpoint<br>
                VMM Cluster Implementation Documentation<br>
                Generated on {{ generation_date }}<br>
                Version 1.0
            </p>
        </div>
    </body>
    </html>
    """
    
    # Prepare data for the template
    context = {
        "config": config,
        "generation_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "logo_base64": logo_base64
    }
    
    # Render the template
    template = jinja2.Template(template_str)
    return template.render(**context)

def generate_powershell_scripts(config):
    """
    Generate PowerShell scripts for VMM cluster implementation.
    
    Args:
        config: Dictionary containing the complete cluster configuration
        
    Returns:
        Dictionary of scripts with their content, organized by category and deployment type
    """
    # Initialize script structure
    scripts = {
        "common": {},
        "hyperv": {},
        "scvmm": {},
        "by_task": {
            "prerequisites": {},
            "network": {},
            "storage": {},
            "cluster": {},
            "security": {}
        },
        "individual_functions": {}  # For storing individual functions/tasks
    }
    
    # 1. Prerequisite Checker Script
    prereq_script = """
# VMM Cluster Implementation - Prerequisite Checker Script
# Generated on {date}

# Check Windows Server version
$osInfo = Get-CimInstance Win32_OperatingSystem
$osVersion = $osInfo.Version
$osName = $osInfo.Caption

Write-Host "Checking operating system..." -ForegroundColor Yellow
if ($osName -like "*Server 2019*" -or $osName -like "*Server 2022*") {{
    Write-Host "OS Check: PASS - $osName" -ForegroundColor Green
}} else {{
    Write-Host "OS Check: FAIL - $osName (Requires Windows Server 2019 or 2022)" -ForegroundColor Red
}}

# Check domain membership
Write-Host "Checking domain membership..." -ForegroundColor Yellow
$computerSystem = Get-CimInstance Win32_ComputerSystem
if ($computerSystem.PartOfDomain) {{
    Write-Host "Domain Membership: PASS - Member of $($computerSystem.Domain)" -ForegroundColor Green
}} else {{
    Write-Host "Domain Membership: FAIL - Not a domain member" -ForegroundColor Red
}}

# Check computer name length
Write-Host "Checking computer name length..." -ForegroundColor Yellow
$computerName = $env:COMPUTERNAME
if ($computerName.Length -le 15) {{
    Write-Host "Computer Name Length: PASS - $computerName ($($computerName.Length) characters)" -ForegroundColor Green
}} else {{
    Write-Host "Computer Name Length: FAIL - $computerName ($($computerName.Length) characters, max is 15)" -ForegroundColor Red
}}

# Check hardware requirements
Write-Host "Checking hardware requirements..." -ForegroundColor Yellow
$processor = Get-CimInstance Win32_Processor
$memory = Get-CimInstance Win32_ComputerSystem
$physicalMemory = [Math]::Round($memory.TotalPhysicalMemory / 1GB, 2)

$procCheckResult = $processor.Count -ge 2 -and $processor[0].NumberOfCores -ge 2
$memCheckResult = $physicalMemory -ge 4

if ($procCheckResult) {{
    Write-Host "Processor Check: PASS - $($processor.Count) processors, $($processor[0].NumberOfCores) cores" -ForegroundColor Green
}} else {{
    Write-Host "Processor Check: FAIL - Requires at least 2 cores" -ForegroundColor Red
}}

if ($memCheckResult) {{
    Write-Host "Memory Check: PASS - $physicalMemory GB RAM" -ForegroundColor Green
}} else {{
    Write-Host "Memory Check: FAIL - Requires at least 4 GB RAM" -ForegroundColor Red
}}

# Check if required features are installed
Write-Host "Checking required Windows features..." -ForegroundColor Yellow

$requiredFeatures = @(
    "Hyper-V",
    "Failover-Clustering",
    "Multipath-IO"
)

foreach ($feature in $requiredFeatures) {{
    $installed = Get-WindowsFeature -Name $feature
    if ($installed.Installed) {{
        Write-Host "Feature $feature: PASS - Installed" -ForegroundColor Green
    }} else {{
        Write-Host "Feature $feature: FAIL - Not installed" -ForegroundColor Red
    }}
}}

# Check Windows ADK
Write-Host "Checking Windows ADK installation..." -ForegroundColor Yellow
$adkPath = "HKLM:\SOFTWARE\Microsoft\Windows Kits\Installed Roots"
if (Test-Path $adkPath) {{
    Write-Host "Windows ADK: PASS - Installed" -ForegroundColor Green
}} else {{
    Write-Host "Windows ADK: FAIL - Not installed" -ForegroundColor Red
}}

# Check network configuration
Write-Host "Checking network configuration..." -ForegroundColor Yellow
$networkAdapters = Get-NetAdapter | Where-Object Status -eq "Up"
if ($networkAdapters.Count -ge 2) {{
    Write-Host "Network Adapters: PASS - $($networkAdapters.Count) connected adapters" -ForegroundColor Green
}} else {{
    Write-Host "Network Adapters: WARNING - Only $($networkAdapters.Count) connected adapters (recommended: at least 2)" -ForegroundColor Yellow
}}

# Summary
Write-Host "`nPrerequisite Check Summary:" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Please review any FAIL or WARNING messages above and address them before proceeding with the VMM cluster implementation."
    """.format(date=datetime.datetime.now().strftime("%Y-%m-%d"))
    
    scripts["01_Prerequisites_Check.ps1"] = prereq_script
    
    # 2. Failover Cluster Setup Script
    cluster_script = """
# VMM Cluster Implementation - Failover Cluster Setup Script
# Generated on {date}

# Parameters
$ClusterName = "{cluster_name}"
$ClusterIP = "{cluster_ip}"
$Nodes = @(
{nodes}
)
$WitnessType = "{witness_type}"  # Options: DiskWitness, FileShareWitness, CloudWitness
$WitnessResource = "{witness_resource}"  # LUN path, file share path, or Azure storage account name

# Install Failover Clustering feature if not already installed
foreach ($node in $Nodes) {{
    Write-Host "Checking Failover Clustering feature on $node..." -ForegroundColor Yellow
    $session = New-PSSession -ComputerName $node
    Invoke-Command -Session $session -ScriptBlock {{
        if (!(Get-WindowsFeature -Name Failover-Clustering).Installed) {{
            Write-Host "Installing Failover Clustering feature on $env:COMPUTERNAME..." -ForegroundColor Yellow
            Install-WindowsFeature -Name Failover-Clustering -IncludeManagementTools
        }} else {{
            Write-Host "Failover Clustering feature already installed on $env:COMPUTERNAME" -ForegroundColor Green
        }}
    }}
    Remove-PSSession $session
}}

# Run cluster validation
Write-Host "Running cluster validation tests..." -ForegroundColor Yellow
Test-Cluster -Node $Nodes -ReportName "$ClusterName-Validation"

# Create the cluster
Write-Host "Creating failover cluster..." -ForegroundColor Yellow
New-Cluster -Name $ClusterName -Node $Nodes -StaticAddress $ClusterIP -NoStorage

# Configure cluster quorum
Write-Host "Configuring cluster quorum..." -ForegroundColor Yellow
switch ($WitnessType) {{
    "DiskWitness" {{
        Set-ClusterQuorum -Cluster $ClusterName -DiskWitness $WitnessResource
    }}
    "FileShareWitness" {{
        Set-ClusterQuorum -Cluster $ClusterName -FileShareWitness $WitnessResource
    }}
    "CloudWitness" {{
        # For Cloud Witness, additional parameters are required
        # This is simplified - you would need to add storage account key and other details
        Set-ClusterQuorum -Cluster $ClusterName -CloudWitness -AccountName $WitnessResource
    }}
}}

# Configure Cluster Shared Volumes if needed
Write-Host "Would you like to configure Cluster Shared Volumes now? (Y/N)" -ForegroundColor Yellow
$configureCSV = Read-Host
if ($configureCSV -eq "Y") {{
    # Get available disks
    $availableDisks = Get-ClusterAvailableDisk -Cluster $ClusterName
    
    if ($availableDisks) {{
        foreach ($disk in $availableDisks) {{
            Add-ClusterDisk -Cluster $ClusterName -InputObject $disk
            $diskName = ($disk | Get-ClusterResource).Name
            Write-Host "Would you like to add $diskName as a CSV? (Y/N)" -ForegroundColor Yellow
            $addAsCSV = Read-Host
            if ($addAsCSV -eq "Y") {{
                Add-ClusterSharedVolume -Cluster $ClusterName -Name $diskName
                Write-Host "Added $diskName as a Cluster Shared Volume" -ForegroundColor Green
            }}
        }}
    }} else {{
        Write-Host "No available disks found for the cluster" -ForegroundColor Yellow
    }}
}}

# Display cluster summary
Write-Host "`nCluster Configuration Summary:" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Cluster Name: $ClusterName"
Write-Host "Cluster IP: $ClusterIP"
Write-Host "Cluster Nodes: $(($Nodes -join ', '))"
Write-Host "Quorum Type: $WitnessType"
Write-Host "`nCluster Resources:" -ForegroundColor Cyan
Get-ClusterResource -Cluster $ClusterName | Format-Table -AutoSize

Write-Host "`nCluster Networks:" -ForegroundColor Cyan
Get-ClusterNetwork -Cluster $ClusterName | Format-Table -AutoSize

Write-Host "`nCluster Shared Volumes:" -ForegroundColor Cyan
Get-ClusterSharedVolume -Cluster $ClusterName | Format-Table -AutoSize
    """.format(
        date=datetime.datetime.now().strftime("%Y-%m-%d"),
        cluster_name=config.get("ha", {}).get("cluster", {}).get("name", "VMM-Cluster"),
        cluster_ip=config.get("ha", {}).get("cluster", {}).get("ip", "192.168.1.100"),
        nodes="\n".join([f'    "{node}"' for node in config.get("hardware", {}).get("servers", [{"name": "Node1"}, {"name": "Node2"}])[:16]]),
        witness_type=config.get("ha", {}).get("cluster", {}).get("witness_type", "DiskWitness"),
        witness_resource=config.get("ha", {}).get("cluster", {}).get("witness_resource", "LUN_PATH")
    )
    
    scripts["02_Failover_Cluster_Setup.ps1"] = cluster_script
    
    # 3. VMM Installation Script
    vmm_script = """
# VMM Cluster Implementation - VMM Installation Script
# Generated on {date}

# Parameters
$VMMServerName = "{vmm_name}"
$ServiceAccountName = "{service_account}"
$ServiceAccountPassword = Read-Host "Enter the service account password" -AsSecureString
$SQLServerName = "{sql_server}"
$SQLInstanceName = "{sql_instance}"
$DKMContainerName = "{dkm_container}"

# Check if SQL Server is accessible
Write-Host "Testing connection to SQL Server..." -ForegroundColor Yellow
$sqlConnection = $SQLServerName
if ($SQLInstanceName -ne "MSSQLSERVER") {{
    $sqlConnection += "\\$SQLInstanceName"
}}

try {{
    $conn = New-Object System.Data.SqlClient.SqlConnection
    $conn.ConnectionString = "Server=$sqlConnection;Integrated Security=True;Connect Timeout=3"
    $conn.Open()
    Write-Host "SQL Server connection successful" -ForegroundColor Green
    $conn.Close()
}} catch {{
    Write-Host "Error connecting to SQL Server: $_" -ForegroundColor Red
    Write-Host "Please verify SQL Server is running and accessible" -ForegroundColor Red
    exit
}}

# Check if DKM container exists in AD
Write-Host "Checking DKM container in Active Directory..." -ForegroundColor Yellow
$adRootDSE = [ADSI]"LDAP://RootDSE"
$defaultNamingContext = $adRootDSE.defaultNamingContext
$dkmPath = "LDAP://CN=$DKMContainerName,CN=System,$defaultNamingContext"

try {{
    $dkmContainer = [ADSI]$dkmPath
    $exists = $dkmContainer.Path -ne $null
    if ($exists) {{
        Write-Host "DKM container exists in AD" -ForegroundColor Green
    }} else {{
        Write-Host "DKM container not found. Creating it now..." -ForegroundColor Yellow
        $systemContainer = [ADSI]"LDAP://CN=System,$defaultNamingContext"
        $newDKM = $systemContainer.Create("container", "CN=$DKMContainerName")
        $newDKM.SetInfo()
        Write-Host "DKM container created successfully" -ForegroundColor Green
    }}
}} catch {{
    Write-Host "Error checking/creating DKM container: $_" -ForegroundColor Red
    Write-Host "Please make sure you have sufficient permissions in Active Directory" -ForegroundColor Red
    exit
}}

# Install VMM prerequisites if not already installed
Write-Host "Checking and installing VMM prerequisites..." -ForegroundColor Yellow

# Check Windows ADK
$adkPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows Kits\\Installed Roots"
if (!(Test-Path $adkPath)) {{
    Write-Host "Windows ADK not found. Please install Windows ADK before continuing." -ForegroundColor Red
    Write-Host "You can download it from: https://docs.microsoft.com/en-us/windows-hardware/get-started/adk-install" -ForegroundColor Yellow
    exit
}}

# Create credential object for service account
$serviceCredential = New-Object System.Management.Automation.PSCredential($ServiceAccountName, $ServiceAccountPassword)

# VMM installation path
Write-Host "Please provide the path to the VMM installation media:" -ForegroundColor Yellow
$vmmMediaPath = Read-Host

if (!(Test-Path $vmmMediaPath)) {{
    Write-Host "Invalid path. Please verify the VMM installation media location." -ForegroundColor Red
    exit
}}

# Installation command
Write-Host "Starting VMM installation..." -ForegroundColor Yellow
$installCmd = "$vmmMediaPath\\Setup.exe /server /i /f /SqlDBName VirtualManagerDB /SqlServerInstance $sqlConnection"
$installCmd += " /VmmServiceDomain $($serviceCredential.UserName.Split('\\')[0])"
$installCmd += " /VmmServiceUserName $($serviceCredential.UserName.Split('\\')[1])"
$installCmd += " /VmmServiceUserPassword $($ServiceAccountPassword)"
$installCmd += " /DKMContainerName $DKMContainerName"
$installCmd += " /IACCEPTSCEULA"

Write-Host "Running installation command: (credentials hidden for security)" -ForegroundColor Yellow
Write-Host "This may take some time. Please wait..." -ForegroundColor Yellow

# Execute installation
try {{
    Invoke-Expression $installCmd
    Write-Host "VMM installation completed successfully" -ForegroundColor Green
}} catch {{
    Write-Host "Error during VMM installation: $_" -ForegroundColor Red
}}

# Check VMM service status
Write-Host "Checking VMM service status..." -ForegroundColor Yellow
$vmmService = Get-Service -Name SCVMMService -ErrorAction SilentlyContinue
if ($vmmService -and $vmmService.Status -eq "Running") {{
    Write-Host "VMM service is running successfully" -ForegroundColor Green
}} else {{
    Write-Host "VMM service is not running. Please check logs for errors." -ForegroundColor Red
}}

Write-Host "`nVMM Installation Summary:" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "VMM Server: $VMMServerName"
Write-Host "SQL Server: $sqlConnection"
Write-Host "Service Account: $ServiceAccountName"
Write-Host "DKM Container: $DKMContainerName"
Write-Host "`nPlease verify all components are working correctly" -ForegroundColor Cyan
    """.format(
        date=datetime.datetime.now().strftime("%Y-%m-%d"),
        vmm_name=config.get("software", {}).get("vmm_server_name", "VMMSERVER"),
        service_account=config.get("software", {}).get("service_account", "DOMAIN\\svc_vmm"),
        sql_server=config.get("software", {}).get("sql_server", "SQLSERVER"),
        sql_instance=config.get("software", {}).get("sql_instance", "MSSQLSERVER"),
        dkm_container=config.get("software", {}).get("dkm_container", "VMMKEK")
    )
    
    scripts["03_VMM_Installation.ps1"] = vmm_script
    
    # 4. High Availability Configuration Script
    ha_script = """
# VMM Cluster Implementation - High Availability Configuration Script
# Generated on {date}

# Parameters
$ClusterName = "{cluster_name}"
$VMMServerName = "{vmm_name}"
$ServiceAccountName = "{service_account}"
$ServiceAccountPassword = Read-Host "Enter the service account password" -AsSecureString
$SQLServerName = "{sql_server}"
$SQLInstanceName = "{sql_instance}"
$DKMContainerName = "{dkm_container}"

# Create credential object for service account
$serviceCredential = New-Object System.Management.Automation.PSCredential($ServiceAccountName, $ServiceAccountPassword)

# Check if VMM is already installed on this node
Write-Host "Checking existing VMM installation..." -ForegroundColor Yellow
$vmmService = Get-Service -Name SCVMMService -ErrorAction SilentlyContinue
if ($vmmService) {{
    Write-Host "VMM is already installed on this node" -ForegroundColor Green
}} else {{
    Write-Host "VMM is not installed on this node. Please run the VMM Installation script first." -ForegroundColor Red
    exit
}}

# Check if Failover Clustering is installed
Write-Host "Checking Failover Clustering feature..." -ForegroundColor Yellow
if (!(Get-WindowsFeature -Name Failover-Clustering).Installed) {{
    Write-Host "Failover Clustering feature is not installed. Installing now..." -ForegroundColor Yellow
    Install-WindowsFeature -Name Failover-Clustering -IncludeManagementTools
}} else {{
    Write-Host "Failover Clustering feature is already installed" -ForegroundColor Green
}}

# Check if node is part of the cluster
Write-Host "Checking if node is part of the cluster..." -ForegroundColor Yellow
try {{
    $nodeInCluster = $false
    $clusterNodes = Get-ClusterNode -Cluster $ClusterName -ErrorAction Stop
    foreach ($node in $clusterNodes) {{
        if ($node.Name -eq $env:COMPUTERNAME) {{
            $nodeInCluster = $true
            break
        }}
    }}
    
    if ($nodeInCluster) {{
        Write-Host "Node is part of the cluster $ClusterName" -ForegroundColor Green
    }} else {{
        Write-Host "Node is not part of the cluster $ClusterName. Adding node to cluster..." -ForegroundColor Yellow
        Add-ClusterNode -Cluster $ClusterName -Name $env:COMPUTERNAME
        Write-Host "Node added to cluster successfully" -ForegroundColor Green
    }}
}} catch {{
    Write-Host "Error checking cluster membership: $_" -ForegroundColor Red
    Write-Host "Please verify the cluster exists and is accessible" -ForegroundColor Red
    exit
}}

# Get VMM media path
Write-Host "Please provide the path to the VMM installation media:" -ForegroundColor Yellow
$vmmMediaPath = Read-Host

if (!(Test-Path $vmmMediaPath)) {{
    Write-Host "Invalid path. Please verify the VMM installation media location." -ForegroundColor Red
    exit
}}

# Configure VMM for high availability
Write-Host "Configuring VMM for high availability..." -ForegroundColor Yellow
$haCmd = "$vmmMediaPath\\Setup.exe /server /ha_install /f"
$haCmd += " /SqlDBName VirtualManagerDB"
$haCmd += " /SqlServerInstance $SQLServerName\\$SQLInstanceName"
$haCmd += " /VMMServiceDomain $($serviceCredential.UserName.Split('\\')[0])"
$haCmd += " /VMMServiceUserName $($serviceCredential.UserName.Split('\\')[1])"
$haCmd += " /VMMServiceUserPassword $($ServiceAccountPassword)"
$haCmd += " /ClusterManagementServer $VMMServerName"
$haCmd += " /ClusterGroupName SCVMM"
$haCmd += " /DKMContainerName $DKMContainerName"
$haCmd += " /IACCEPTSCEULA"

Write-Host "Running high availability configuration command: (credentials hidden for security)" -ForegroundColor Yellow
Write-Host "This may take some time. Please wait..." -ForegroundColor Yellow

# Execute HA configuration
try {{
    Invoke-Expression $haCmd
    Write-Host "VMM high availability configuration completed successfully" -ForegroundColor Green
}} catch {{
    Write-Host "Error during VMM high availability configuration: $_" -ForegroundColor Red
}}

# Check VMM cluster resource status
Write-Host "Checking VMM cluster resource status..." -ForegroundColor Yellow
$vmmResource = Get-ClusterResource -Cluster $ClusterName | Where-Object {{$_.ResourceType -eq "Virtual Machine Manager Server"}}
if ($vmmResource) {{
    Write-Host "VMM cluster resource exists and is in $($vmmResource.State) state" -ForegroundColor Green
    if ($vmmResource.State -ne "Online") {{
        Write-Host "Starting VMM cluster resource..." -ForegroundColor Yellow
        Start-ClusterResource -Name $vmmResource.Name
        Write-Host "VMM cluster resource started" -ForegroundColor Green
    }}
}} else {{
    Write-Host "VMM cluster resource not found. Please check the high availability configuration." -ForegroundColor Red
}}

Write-Host "`nVMM High Availability Configuration Summary:" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Cluster Name: $ClusterName"
Write-Host "VMM Server: $VMMServerName"
Write-Host "SQL Server: $SQLServerName\\$SQLInstanceName"
Write-Host "Service Account: $ServiceAccountName"
Write-Host "DKM Container: $DKMContainerName"
Write-Host "`nPlease verify the VMM cluster resource is online and functioning correctly" -ForegroundColor Cyan
Write-Host "You should now be able to connect to the VMM server using the cluster name" -ForegroundColor Cyan
    """.format(
        date=datetime.datetime.now().strftime("%Y-%m-%d"),
        cluster_name=config.get("ha", {}).get("cluster", {}).get("name", "VMM-Cluster"),
        vmm_name=config.get("software", {}).get("vmm_server_name", "VMMSERVER"),
        service_account=config.get("software", {}).get("service_account", "DOMAIN\\svc_vmm"),
        sql_server=config.get("software", {}).get("sql_server", "SQLSERVER"),
        sql_instance=config.get("software", {}).get("sql_instance", "MSSQLSERVER"),
        dkm_container=config.get("software", {}).get("dkm_container", "VMMKEK")
    )
    
    scripts["04_High_Availability_Configuration.ps1"] = ha_script
    
    # 5. Network Configuration Script
    network_script = """
# VMM Cluster Implementation - Network Configuration Script
# Generated on {date}

# Parameters
$VMMServer = "{vmm_server}"
$LogicalNetworks = @(
{logical_networks}
)
$VMNetworks = @(
{vm_networks}
)

# Connect to VMM server
Write-Host "Connecting to VMM server $VMMServer..." -ForegroundColor Yellow
try {{
    Import-Module VirtualMachineManager
    Get-SCVMMServer -ComputerName $VMMServer
    Write-Host "Connected to VMM server successfully" -ForegroundColor Green
}} catch {{
    Write-Host "Error connecting to VMM server: $_" -ForegroundColor Red
    Write-Host "Please make sure the VMM server is accessible and you have the VMM console installed" -ForegroundColor Red
    exit
}}

# Create logical networks
Write-Host "Creating logical networks..." -ForegroundColor Yellow
foreach ($network in $LogicalNetworks) {{
    Write-Host "Processing logical network: $($network.Name)" -ForegroundColor Yellow
    
    # Check if logical network already exists
    $existingNetwork = Get-SCLogicalNetwork -Name $network.Name -ErrorAction SilentlyContinue
    
    if ($existingNetwork) {{
        Write-Host "Logical network $($network.Name) already exists" -ForegroundColor Yellow
    }} else {{
        # Create new logical network
        Write-Host "Creating logical network $($network.Name)..." -ForegroundColor Yellow
        $newNetwork = New-SCLogicalNetwork -Name $network.Name -Description $network.Description -EnableNetworkVirtualization $network.EnableNetworkVirtualization
        
        # Create network sites
        foreach ($site in $network.Sites) {{
            Write-Host "Creating network site $($site.Name) in $($network.Name)..." -ForegroundColor Yellow
            
            # Get host group
            $hostGroup = Get-SCVMHostGroup -Name $site.HostGroup -ErrorAction SilentlyContinue
            if (!$hostGroup) {{
                Write-Host "Host group $($site.HostGroup) not found. Creating it..." -ForegroundColor Yellow
                $hostGroup = New-SCVMHostGroup -Name $site.HostGroup
            }}
            
            # Create the network site
            $networkSite = New-SCLogicalNetworkDefinition -Name $site.Name -LogicalNetwork $newNetwork -VMHostGroup $hostGroup
            
            # Add subnets to the network site
            foreach ($subnet in $site.Subnets) {{
                Write-Host "Adding subnet $($subnet.Subnet) to network site $($site.Name)..." -ForegroundColor Yellow
                $vlanID = if ($subnet.VLAN -ne $null) {{ $subnet.VLAN }} else {{ 0 }}
                Set-SCLogicalNetworkDefinition -LogicalNetworkDefinition $networkSite -SubnetVLan $subnet.Subnet, $vlanID
            }}
        }}
        
        Write-Host "Logical network $($network.Name) created successfully" -ForegroundColor Green
    }}
}}

# Create VM networks
Write-Host "Creating VM networks..." -ForegroundColor Yellow
foreach ($vmNetwork in $VMNetworks) {{
    Write-Host "Processing VM network: $($vmNetwork.Name)" -ForegroundColor Yellow
    
    # Check if VM network already exists
    $existingVMNetwork = Get-SCVMNetwork -Name $vmNetwork.Name -ErrorAction SilentlyContinue
    
    if ($existingVMNetwork) {{
        Write-Host "VM network $($vmNetwork.Name) already exists" -ForegroundColor Yellow
    }} else {{
        # Get the logical network
        $logicalNetwork = Get-SCLogicalNetwork -Name $vmNetwork.LogicalNetwork -ErrorAction SilentlyContinue
        
        if (!$logicalNetwork) {{
            Write-Host "Logical network $($vmNetwork.LogicalNetwork) not found. Skipping VM network creation." -ForegroundColor Red
            continue
        }}
        
        # Create the VM network
        Write-Host "Creating VM network $($vmNetwork.Name)..." -ForegroundColor Yellow
        if ($vmNetwork.Isolated) {{
            # Create isolated VM network
            $newVMNetwork = New-SCVMNetwork -Name $vmNetwork.Name -Description $vmNetwork.Description -LogicalNetwork $logicalNetwork -IsolationType "WindowsNetworkVirtualization"
        }} else {{
            # Create regular VM network
            $newVMNetwork = New-SCVMNetwork -Name $vmNetwork.Name -Description $vmNetwork.Description -LogicalNetwork $logicalNetwork
        }}
        
        Write-Host "VM network $($vmNetwork.Name) created successfully" -ForegroundColor Green
    }}
}}

# Configure logical switches if requested
Write-Host "Would you like to configure logical switches now? (Y/N)" -ForegroundColor Yellow
$configureSwitches = Read-Host

if ($configureSwitches -eq "Y") {{
    $switchName = Read-Host "Enter logical switch name"
    $switchDesc = Read-Host "Enter logical switch description"
    
    # Create the logical switch
    Write-Host "Creating logical switch $switchName..." -ForegroundColor Yellow
    $newSwitch = New-SCLogicalSwitch -Name $switchName -Description $switchDesc -EnableSriov $false -SwitchUplinkMode "TeamUplink"
    
    # Create uplink port profile
    $uplinkProfileName = "$switchName-Uplink"
    Write-Host "Creating uplink port profile $uplinkProfileName..." -ForegroundColor Yellow
    $newUplinkProfile = New-SCNativeUplinkPortProfile -Name $uplinkProfileName -Description "Uplink port profile for $switchName" -EnableNetworkVirtualization $false -LBFOLoadBalancingAlgorithm "HostDefault" -LBFOTeamMode "SwitchIndependent"
    
    # Create NIC port profiles
    Write-Host "Creating NIC port profiles..." -ForegroundColor Yellow
    $managementProfile = New-SCNativeUplinkPortProfile -Name "$switchName-Management" -Description "Management network port profile" -EnableNetworkVirtualization $false
    $vmProfile = New-SCNativeUplinkPortProfile -Name "$switchName-VM" -Description "VM network port profile" -EnableNetworkVirtualization $true
    
    # Add uplink port profile to logical switch
    Write-Host "Adding uplink port profile to logical switch..." -ForegroundColor Yellow
    Add-SCLogicalSwitchUplinkPortProfile -LogicalSwitch $newSwitch -NativeUplinkPortProfile $newUplinkProfile
    
    Write-Host "Logical switch $switchName created successfully" -ForegroundColor Green
}}

Write-Host "`nNetwork Configuration Summary:" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host "Logical Networks:"
Get-SCLogicalNetwork | Format-Table -Property Name, Description

Write-Host "`nVM Networks:"
Get-SCVMNetwork | Format-Table -Property Name, LogicalNetwork, Description

Write-Host "`nLogical Switches:"
Get-SCLogicalSwitch | Format-Table -Property Name, Description

Write-Host "`nPlease verify all network components have been created correctly" -ForegroundColor Cyan
    """.format(
        date=datetime.datetime.now().strftime("%Y-%m-%d"),
        vmm_server=config.get("software", {}).get("vmm_server_name", "VMMSERVER"),
        logical_networks="\n".join([
            f"""    @{{
        Name = "{net.get('name', f'LogicalNetwork{i+1}')}";
        Description = "{net.get('description', f'Logical Network {i+1}')}";
        EnableNetworkVirtualization = ${str(net.get('network_virtualization', False)).lower()};
        Sites = @(
            @{{
                Name = "{net.get('name', f'LogicalNetwork{i+1}')}Site";
                HostGroup = "All Hosts";
                Subnets = @(
                    @{{
                        Subnet = "{net.get('cidr', '192.168.1.0/24')}";
                        VLAN = {net.get('vlan', 0)};
                    }}
                )
            }}
        )
    }}""" 
            for i, net in enumerate(config.get("network", {}).get("logical_networks", [
                {"name": "Management", "cidr": "192.168.1.0/24", "vlan": 0},
                {"name": "LiveMigration", "cidr": "192.168.2.0/24", "vlan": 10},
                {"name": "VM", "cidr": "192.168.3.0/24", "vlan": 20}
            ]))
        ]),
        vm_networks="\n".join([
            f"""    @{{
        Name = "{net.get('name', f'VMNetwork{i+1}')}";
        Description = "{net.get('description', f'VM Network {i+1}')}";
        LogicalNetwork = "{net.get('logical_network', 'VM')}";
        Isolated = ${str(net.get('isolated', False)).lower()};
    }}"""
            for i, net in enumerate(config.get("network", {}).get("vm_networks", [
                {"name": "VM Network", "logical_network": "VM", "isolated": False}
            ]))
        ])
    )
    
    scripts["05_Network_Configuration.ps1"] = network_script
    
    return scripts

def convert_image_to_base64(fig):
    """
    Convert a Plotly figure to a base64 encoded string.
    
    Args:
        fig: Plotly figure object
        
    Returns:
        Base64 encoded string of the image
    """
    img_bytes = pio.to_image(fig, format="png")
    img_base64 = base64.b64encode(img_bytes).decode('ascii')
    return img_base64

def export_documentation_to_file(html_content, filename="VMM_Cluster_Documentation.html"):
    """
    Export the generated HTML documentation to a file.
    
    Args:
        html_content: HTML content string
        filename: Output filename
        
    Returns:
        Path to the saved file
    """
    output_path = os.path.join(os.getcwd(), filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path

def export_scripts_to_files(scripts, directory="implementation_scripts"):
    """
    Export the generated PowerShell scripts to files.
    
    Args:
        scripts: Dictionary of script names and content
        directory: Output directory
        
    Returns:
        Path to the script directory
    """
    output_dir = os.path.join(os.getcwd(), directory)
    os.makedirs(output_dir, exist_ok=True)
    
    for script_name, script_content in scripts.items():
        script_path = os.path.join(output_dir, script_name)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
    
    return output_dir
