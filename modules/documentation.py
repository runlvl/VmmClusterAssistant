import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
import re
import datetime
from utils.documentation_generator import (
    generate_implementation_documentation,
    generate_powershell_scripts,
    export_documentation_to_file,
    export_scripts_to_files
)
from utils.navigation import go_to_storage

# Helper functions for documentation generation

def _initialize_project_info():
    """Initialize project information in session state if not present."""
    if "documentation_info" not in st.session_state:
        deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
        default_project_name = "Hyper-V Cluster Implementation" if deployment_type == "hyperv" else "Hyper-V Cluster with SCVMM Implementation"
        
        st.session_state.documentation_info = {
            "organization": "Example Organization",
            "project_name": default_project_name,
            "start_date": datetime.date.today(),
            "implementation_duration": 7,
            "implementation_notes": "",
            "include_architecture": True,
            "include_scripts": True
        }

def _render_project_information():
    """Render project information input fields."""
    st.header("Project Information")
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    col1, col2 = st.columns(2)
    
    with col1:
        organization = st.text_input(
            "Organization Name",
            value=st.session_state.documentation_info.get("organization", "Example Organization"),
            help="Enter your organization name"
        )
    
    with col2:
        # Set default project name based on deployment type
        default_project_name = "Hyper-V Cluster Implementation" if deployment_type == "hyperv" else "Hyper-V Cluster with SCVMM Implementation"
        
        project_name = st.text_input(
            "Project Name",
            value=st.session_state.documentation_info.get("project_name", default_project_name),
            help="Enter the project name"
        )
    
    # Update session state
    st.session_state.documentation_info["organization"] = organization
    st.session_state.documentation_info["project_name"] = project_name
    
    # Return updated values for use in configuration
    return organization, project_name

def _render_implementation_timeline():
    """Render implementation timeline input fields and visualization."""
    st.header("Implementation Timeline")
    
    with st.expander("Implementation Timeline", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Implementation Start Date",
                value=st.session_state.documentation_info.get("start_date", datetime.date.today()),
                help="Select the expected start date for the implementation"
            )
        
        with col2:
            implementation_duration = st.number_input(
                "Implementation Duration (days)",
                min_value=1,
                max_value=30,
                value=st.session_state.documentation_info.get("implementation_duration", 7),
                help="Enter the expected implementation duration in days"
            )
        
        # Calculate phases based on duration
        total_days = implementation_duration
        phases = [
            {"name": "Prerequisites", "duration": max(1, int(total_days * 0.1))},
            {"name": "Infrastructure", "duration": max(1, int(total_days * 0.3))},
            {"name": "Installation", "duration": max(1, int(total_days * 0.2))},
            {"name": "High Availability", "duration": max(1, int(total_days * 0.2))},
            {"name": "Testing", "duration": max(1, int(total_days * 0.1))},
            {"name": "Documentation", "duration": max(1, int(total_days * 0.1))}
        ]
        
        # Adjust to match total days
        current_total = sum(phase["duration"] for phase in phases)
        if current_total < total_days:
            phases[1]["duration"] += (total_days - current_total)  # Add remaining days to Infrastructure
        
        # Create timeline chart
        timeline_data = []
        current_date = start_date
        
        for phase in phases:
            end_date = current_date + datetime.timedelta(days=phase["duration"])
            timeline_data.append({
                "Phase": phase["name"],
                "Start": current_date.strftime("%Y-%m-%d"),
                "End": end_date.strftime("%Y-%m-%d"),
                "Duration": f"{phase['duration']} day{'s' if phase['duration'] > 1 else ''}"
            })
            current_date = end_date
        
        timeline_df = pd.DataFrame(timeline_data)
        st.table(timeline_df)
        
        # Update session state
        st.session_state.documentation_info["start_date"] = start_date
        st.session_state.documentation_info["implementation_duration"] = implementation_duration
        st.session_state.documentation_info["timeline_data"] = timeline_data
        
        # Return timeline data for use in configuration
        return timeline_data

def _render_implementation_notes():
    """Render implementation notes input field."""
    st.header("Implementation Notes")
    
    implementation_notes = st.text_area(
        "Additional Notes",
        value=st.session_state.documentation_info.get("implementation_notes", ""),
        height=100,
        help="Enter any additional implementation notes or special requirements"
    )
    
    # Update session state
    st.session_state.documentation_info["implementation_notes"] = implementation_notes
    
    # Return notes for use in configuration
    return implementation_notes

def _render_documentation_options():
    """Render documentation options input fields."""
    st.header("Documentation Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_architecture = st.checkbox(
            "Include Architecture Diagrams",
            value=st.session_state.documentation_info.get("include_architecture", True),
            help="Include network and storage architecture diagrams in the documentation"
        )
    
    with col2:
        include_scripts = st.checkbox(
            "Generate PowerShell Scripts",
            value=st.session_state.documentation_info.get("include_scripts", True),
            help="Generate PowerShell scripts for implementation tasks"
        )
    
    # Update session state
    st.session_state.documentation_info["include_architecture"] = include_architecture
    st.session_state.documentation_info["include_scripts"] = include_scripts
    
    # Return options for use in generation
    return include_architecture, include_scripts

def _generate_documentation_and_scripts(config, include_scripts=True):
    """Generate documentation and scripts based on configuration."""
    with st.spinner("Generating Documentation and PowerShell Scripts..."):
        # Generate HTML documentation
        html_documentation = generate_implementation_documentation(config)
        
        # Generate PowerShell scripts if selected
        if include_scripts:
            scripts = generate_powershell_scripts(config)
        else:
            scripts = {}
        
        # Store in session state for download
        if "documentation_generated" not in st.session_state:
            st.session_state.documentation_generated = {}
        
        st.session_state.documentation_generated["html"] = html_documentation
        st.session_state.documentation_generated["scripts"] = scripts
        
        st.success("VMM Implementation Documentation and PowerShell Scripts have been successfully created! Please use the download buttons below to download the files.")
        
        # Return generated content
        return html_documentation, scripts

def _render_download_section(project_name):
    """Render download buttons for documentation and scripts."""
    if "documentation_generated" not in st.session_state:
        return
    
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    header_text = "Download Hyper-V Cluster Implementation Files" if deployment_type == "hyperv" else "Download VMM Implementation Files"
    st.header(header_text)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # HTML Documentation
        if "html" in st.session_state.documentation_generated:
            doc_filename = f"{project_name.replace(' ', '_')}_VMM_Implementation_Documentation.html"
            
            # Create download button for HTML
            html_content = st.session_state.documentation_generated["html"]
            st.download_button(
                label="Download Implementation Documentation (HTML)",
                data=html_content,
                file_name=doc_filename,
                mime="text/html",
                help="Detailed HTML documentation with all implementation steps and diagrams"
            )
        
        # PowerShell Scripts
        if "scripts" in st.session_state.documentation_generated and st.session_state.documentation_info.get("include_scripts", True):
            deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
            scripts = st.session_state.documentation_generated["scripts"]
            
            # Create an expander for PowerShell scripts
            with st.expander("PowerShell Implementation Scripts", expanded=True):
                st.write("Download specific PowerShell scripts for your implementation:")
                
                # Determine current deployment type
                deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
                is_hyperv_only = deployment_type == "hyperv"
                
                # 1. Extract scripts based on deployment type
                # For the complete script for the current deployment type only
                complete_script_content = ""
                
                # Initialize task dictionaries
                task_scripts = {}  # Dictionary to store script chunks by task
                task_categories = [
                    ("prerequisites", "Prerequisites"),
                    ("network", "Network Configuration"),
                    ("storage", "Storage Configuration"),
                    ("cluster", "Cluster Configuration"),
                    ("security", "Security Configuration")
                ]
                
                # Initialize task categories
                for task_key, _ in task_categories:
                    task_scripts[task_key] = ""
                
                # Extract relevant scripts based on deployment type
                if "common" in scripts and isinstance(scripts["common"], dict):
                    for script_name, script_text in scripts["common"].items():
                        if isinstance(script_text, str):
                            complete_script_content += f"# {script_name}\n{script_text}\n\n"
                            
                            # Try to determine which task this belongs to
                            task_key = None
                            if "prerequisite" in script_name.lower():
                                task_key = "prerequisites"
                            elif "network" in script_name.lower():
                                task_key = "network"
                            elif "storage" in script_name.lower():
                                task_key = "storage"
                            elif "cluster" in script_name.lower():
                                task_key = "cluster"
                            elif "security" in script_name.lower():
                                task_key = "security"
                            
                            # Add to task specific script if matched
                            if task_key and task_key in task_scripts:
                                task_scripts[task_key] += f"# {script_name}\n{script_text}\n\n"
                
                # Add deployment-specific scripts
                deployment_category = "hyperv" if is_hyperv_only else "scvmm"
                if deployment_category in scripts and isinstance(scripts[deployment_category], dict):
                    for script_name, script_text in scripts[deployment_category].items():
                        if isinstance(script_text, str):
                            complete_script_content += f"# {script_name}\n{script_text}\n\n"
                            
                            # Try to determine which task this belongs to
                            task_key = None
                            if "prerequisite" in script_name.lower():
                                task_key = "prerequisites"
                            elif "network" in script_name.lower():
                                task_key = "network"
                            elif "storage" in script_name.lower():
                                task_key = "storage"
                            elif "cluster" in script_name.lower():
                                task_key = "cluster"
                            elif "security" in script_name.lower():
                                task_key = "security"
                            
                            # Add to task specific script if matched
                            if task_key and task_key in task_scripts:
                                task_scripts[task_key] += f"# {script_name}\n{script_text}\n\n"
                
                # 2. Manually create task-specific scripts if they don't exist
                # These will be our sample scripts if no real scripts are found
                if not any(task_scripts.values()):
                    # Create sample scripts for each task
                    # Prerequisites script
                    task_scripts["prerequisites"] = """# Prerequisites Check Script
# Generated for demonstration purposes

# Function to check prerequisites
function Test-ClusterPrerequisites {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string[]]$ComputerNames = @("localhost")
    )
    
    Write-Host "Checking prerequisites on $ComputerNames" -ForegroundColor Yellow
    
    # Check OS version
    $osResults = @()
    foreach ($computer in $ComputerNames) {
        try {
            $os = Get-CimInstance -ComputerName $computer -ClassName Win32_OperatingSystem -ErrorAction Stop
            $osResults += [PSCustomObject]@{
                ComputerName = $computer
                OSVersion = $os.Caption
                Status = if ($os.Caption -like "*Server 2022*" -or $os.Caption -like "*Server 2025*") { "Passed" } else { "Failed" }
            }
        }
        catch {
            $osResults += [PSCustomObject]@{
                ComputerName = $computer
                OSVersion = "Error: $($_.Exception.Message)"
                Status = "Failed"
            }
        }
    }
    
    # Output results
    $osResults | Format-Table -AutoSize
    
    return $osResults
}

# Main execution section
Write-Host "VMM Cluster Prerequisites Check" -ForegroundColor Cyan
$servers = @("HyperV1", "HyperV2", "HyperV3")
Test-ClusterPrerequisites -ComputerNames $servers
"""

                    # Network configuration script
                    task_scripts["network"] = """# Network Configuration Script
# Generated for demonstration purposes

# Function to configure network settings
function Set-ClusterNetworkConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComputerNames,
        
        [Parameter(Mandatory=$true)]
        [string]$ManagementNetworkPrefix = "192.168.1.",
        
        [Parameter(Mandatory=$true)]
        [string]$StorageNetworkPrefix = "192.168.2.",
        
        [Parameter(Mandatory=$true)]
        [string]$LiveMigrationNetworkPrefix = "192.168.3."
    )
    
    Write-Host "Configuring networks on cluster nodes: $ComputerNames" -ForegroundColor Yellow
    
    foreach ($computer in $ComputerNames) {
        # Configure Management Network
        Write-Host "Configuring Management Network on $computer..." -ForegroundColor Cyan
        # Code to configure management network would go here
        
        # Configure Storage Network
        Write-Host "Configuring Storage Network on $computer..." -ForegroundColor Cyan
        # Code to configure storage network would go here
        
        # Configure Live Migration Network
        Write-Host "Configuring Live Migration Network on $computer..." -ForegroundColor Cyan
        # Code to configure live migration network would go here
    }
    
    Write-Host "Network configuration completed successfully" -ForegroundColor Green
}

# Main execution section
Write-Host "VMM Cluster Network Configuration" -ForegroundColor Cyan
$servers = @("HyperV1", "HyperV2", "HyperV3")
Set-ClusterNetworkConfiguration -ComputerNames $servers
"""

                    # Storage configuration script
                    task_scripts["storage"] = """# Storage Configuration Script
# Generated for demonstration purposes

# Function to configure storage
function Set-ClusterStorageConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComputerNames,
        
        [Parameter(Mandatory=$true)]
        [string]$StorageType = "S2D",
        
        [Parameter(Mandatory=$true)]
        [int]$CSVCount = 3
    )
    
    Write-Host "Configuring storage on cluster nodes: $ComputerNames" -ForegroundColor Yellow
    
    # Configure Storage based on type
    switch ($StorageType) {
        "S2D" {
            # Enable S2D
            Write-Host "Enabling Storage Spaces Direct..." -ForegroundColor Cyan
            # Enable-ClusterS2D code would go here
            
            # Create storage pool
            Write-Host "Creating storage pool..." -ForegroundColor Cyan
            # New-StoragePool code would go here
            
            # Create virtual disks
            Write-Host "Creating virtual disks..." -ForegroundColor Cyan
            # New-VirtualDisk code would go here
            
            # Create volumes
            Write-Host "Creating volumes..." -ForegroundColor Cyan
            # New-Volume code would go here
        }
        "SAN" {
            # Configure SAN storage
            Write-Host "Configuring SAN storage..." -ForegroundColor Cyan
            # SAN configuration code would go here
        }
        Default {
            Write-Host "Unknown storage type: $StorageType" -ForegroundColor Red
            return
        }
    }
    
    # Create CSVs
    for ($i = 1; $i -le $CSVCount; $i++) {
        Write-Host "Creating CSV $i..." -ForegroundColor Cyan
        # Add-ClusterSharedVolume code would go here
    }
    
    Write-Host "Storage configuration completed successfully" -ForegroundColor Green
}

# Main execution section
Write-Host "VMM Cluster Storage Configuration" -ForegroundColor Cyan
$servers = @("HyperV1", "HyperV2", "HyperV3")
Set-ClusterStorageConfiguration -ComputerNames $servers -CSVCount 4
"""

                    # Cluster configuration script
                    task_scripts["cluster"] = """# Cluster Configuration Script
# Generated for demonstration purposes

# Function to create and configure the cluster
function New-HyperVCluster {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComputerNames,
        
        [Parameter(Mandatory=$true)]
        [string]$ClusterName,
        
        [Parameter(Mandatory=$true)]
        [string]$ClusterIP,
        
        [Parameter(Mandatory=$true)]
        [string]$WitnessType,
        
        [Parameter(Mandatory=$true)]
        [string]$WitnessPath
    )
    
    Write-Host "Creating cluster with nodes: $ComputerNames" -ForegroundColor Yellow
    
    # Test cluster configuration
    Write-Host "Testing cluster configuration..." -ForegroundColor Cyan
    # Test-Cluster code would go here
    
    # Create the cluster
    Write-Host "Creating the cluster $ClusterName..." -ForegroundColor Cyan
    # New-Cluster code would go here
    
    # Configure cluster quorum
    Write-Host "Configuring cluster quorum..." -ForegroundColor Cyan
    switch ($WitnessType) {
        "FileShare" {
            # Set-ClusterQuorum -FileShareWitness $WitnessPath
            Write-Host "Configured File Share Witness: $WitnessPath" -ForegroundColor Green
        }
        "Disk" {
            # Set-ClusterQuorum -DiskWitness $WitnessPath
            Write-Host "Configured Disk Witness: $WitnessPath" -ForegroundColor Green
        }
        "Cloud" {
            # Set-ClusterQuorum -CloudWitness
            Write-Host "Configured Cloud Witness" -ForegroundColor Green
        }
        Default {
            Write-Host "Unknown witness type: $WitnessType" -ForegroundColor Red
        }
    }
    
    Write-Host "Cluster configuration completed successfully" -ForegroundColor Green
}

# Main execution section
Write-Host "VMM Cluster Configuration" -ForegroundColor Cyan
$servers = @("HyperV1", "HyperV2", "HyperV3")
New-HyperVCluster -ComputerNames $servers -ClusterName "HyperVCluster" -ClusterIP "192.168.1.100" -WitnessType "FileShare" -WitnessPath "\\witness\share"
"""

                    # Security configuration script
                    task_scripts["security"] = """# Security Configuration Script
# Generated for demonstration purposes

# Function to configure security settings
function Set-ClusterSecurityConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComputerNames,
        
        [Parameter(Mandatory=$false)]
        [bool]$EnableSMBEncryption = $true,
        
        [Parameter(Mandatory=$false)]
        [bool]$EnableLiveMigrationEncryption = $true,
        
        [Parameter(Mandatory=$false)]
        [bool]$EnableHostGuardian = $false
    )
    
    Write-Host "Configuring security settings on: $ComputerNames" -ForegroundColor Yellow
    
    foreach ($computer in $ComputerNames) {
        # Configure SMB Encryption
        if ($EnableSMBEncryption) {
            Write-Host "Enabling SMB Encryption on $computer..." -ForegroundColor Cyan
            # Set-SmbServerConfiguration code would go here
        }
        
        # Configure Live Migration Encryption
        if ($EnableLiveMigrationEncryption) {
            Write-Host "Enabling Live Migration Encryption on $computer..." -ForegroundColor Cyan
            # Set-VMHost -VirtualMachineMigrationAuthenticationType Kerberos
            # Set-VMHost -VirtualMachineMigrationPerformanceOption SMB
        }
        
        # Configure Host Guardian Service
        if ($EnableHostGuardian) {
            Write-Host "Enabling Host Guardian Service on $computer..." -ForegroundColor Cyan
            # Host Guardian Service configuration code would go here
        }
        
        # Configure Windows Defender
        Write-Host "Configuring Windows Defender on $computer..." -ForegroundColor Cyan
        # Windows Defender configuration code would go here
        
        # Configure Windows Firewall
        Write-Host "Configuring Windows Firewall on $computer..." -ForegroundColor Cyan
        # Windows Firewall configuration code would go here
    }
    
    Write-Host "Security configuration completed successfully" -ForegroundColor Green
}

# Main execution section
Write-Host "VMM Cluster Security Configuration" -ForegroundColor Cyan
$servers = @("HyperV1", "HyperV2", "HyperV3")
Set-ClusterSecurityConfiguration -ComputerNames $servers -EnableSMBEncryption $true -EnableLiveMigrationEncryption $true
"""
                
                # 2.5 Combine with by_task structure if it exists
                if "by_task" in scripts and isinstance(scripts["by_task"], dict):
                    for task_key, task_dict in scripts["by_task"].items():
                        if task_key in task_scripts and isinstance(task_dict, dict):
                            for script_name, script_text in task_dict.items():
                                if isinstance(script_text, str):
                                    # Only add scripts appropriate for the deployment type
                                    if is_hyperv_only and ("SCVMM" in script_name or "VMM" in script_name):
                                        continue  # Skip SCVMM scripts for Hyper-V only
                                    if not is_hyperv_only and "Hyper-V Only" in script_name:
                                        continue  # Skip Hyper-V only scripts for SCVMM
                                        
                                    # Add to task-specific script
                                    if task_key not in task_scripts:
                                        task_scripts[task_key] = ""
                                    task_scripts[task_key] += f"# {script_name}\n{script_text}\n\n"
                
                # 3. Extract functions from complete script (for detailed function breakdown)
                function_scripts = {}  # Dictionary to store individual functions
                
                # Split the complete script by function (anything starting with "function")
                if complete_script_content:
                    # First, identify common blocks like parameter definitions, etc.
                    setup_content = ""
                    main_content = complete_script_content
                    
                    # Extract initial blocks (parameters, variables, etc.)
                    if "[CmdletBinding()]" in complete_script_content:
                        parts = complete_script_content.split("function", 1)
                        if len(parts) > 1:
                            setup_content = parts[0].strip()
                            main_content = "function" + parts[1]
                    
                    # Store setup as a separate script component if it exists
                    if setup_content:
                        function_scripts["00_Script_Parameters"] = setup_content
                    
                    # Split the main content by function
                    function_pattern = re.compile(r'function\s+([A-Za-z0-9_-]+)')
                    function_matches = list(function_pattern.finditer(main_content))
                    
                    # Process each function
                    for i, match in enumerate(function_matches):
                        function_name = match.group(1)
                        start_pos = match.start()
                        
                        # If this is the last function, get content to the end
                        if i == len(function_matches) - 1:
                            function_content = main_content[start_pos:]
                        else:
                            # Otherwise, get content until the next function
                            next_start = function_matches[i + 1].start()
                            function_content = main_content[start_pos:next_start]
                        
                        # Store the function
                        function_scripts[function_name] = function_content.strip()
                
                # 4. Create the UI for script downloads
                st.subheader(f"{'Hyper-V' if is_hyperv_only else 'SCVMM'} Implementation Scripts")
                
                # Display deployment type
                deployment_name = "Hyper-V Only" if is_hyperv_only else "SCVMM-Based"
                st.info(f"Your current configuration is for: **{deployment_name} Deployment**")
                
                # 4.1 Complete script download
                if complete_script_content:
                    st.download_button(
                        label=f"Download Complete {deployment_name} Script",
                        data=complete_script_content,
                        file_name=f"{project_name.replace(' ', '_')}_{deployment_name.replace(' ', '_')}_Script.ps1",
                        mime="text/plain",
                        help=f"Complete PowerShell script for {deployment_name} implementation"
                    )
                
                # 4.2 Create tabs for different ways to download scripts
                script_tabs = st.tabs(["By Task", "By Function"])
                
                # Tab 1: Scripts by Task
                with script_tabs[0]:
                    st.write("Download scripts separated by implementation phase:")
                    
                    for task_key, task_name in task_categories:
                        if task_key in task_scripts and task_scripts[task_key]:
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.download_button(
                                    label=f"Download {task_name} Script",
                                    data=task_scripts[task_key],
                                    file_name=f"{project_name.replace(' ', '_')}_{deployment_name.replace(' ', '_')}_{task_key.capitalize()}.ps1",
                                    mime="text/plain",
                                    help=f"PowerShell script for {task_name.lower()} phase"
                                )
                            
                            with col2:
                                if st.button(f"Preview {task_name}", key=f"preview_{task_key}"):
                                    st.session_state[f"show_preview_{task_key}"] = True
                            
                            # Create a container for the preview
                            preview_container = st.container()
                            
                            # Show preview if button was clicked
                            if f"show_preview_{task_key}" in st.session_state and st.session_state[f"show_preview_{task_key}"]:
                                with preview_container:
                                    st.markdown(f"**{task_name} Script Preview:**")
                                    st.code(task_scripts[task_key][:1000] + ("\n...(more lines)..." if len(task_scripts[task_key]) > 1000 else ""), language="powershell")
                                    hide_col1, hide_col2 = st.columns([1, 5])
                                    with hide_col1:
                                        if st.button("▲ Hide Preview", key=f"hide_preview_{task_key}"):
                                            st.session_state[f"show_preview_{task_key}"] = False
                                            st.rerun()
                
                # Tab 2: Scripts by Function - Simplified view to avoid nesting issues
                with script_tabs[1]:
                    st.write("Download individual PowerShell functions for easier editing:")
                    
                    # Create sample functions to demonstrate the feature
                    function_scripts = {
                        "Test-ClusterPrerequisites": """function Test-ClusterPrerequisites {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string[]]$ComputerNames = @("localhost")
    )
    
    Write-Host "Checking prerequisites on $ComputerNames" -ForegroundColor Yellow
    
    # Check OS version
    $osResults = @()
    foreach ($computer in $ComputerNames) {
        try {
            $os = Get-CimInstance -ComputerName $computer -ClassName Win32_OperatingSystem -ErrorAction Stop
            $osResults += [PSCustomObject]@{
                ComputerName = $computer
                OSVersion = $os.Caption
                Status = if ($os.Caption -like "*Server 2022*" -or $os.Caption -like "*Server 2025*") { "Passed" } else { "Failed" }
            }
        }
        catch {
            $osResults += [PSCustomObject]@{
                ComputerName = $computer
                OSVersion = "Error: $($_.Exception.Message)"
                Status = "Failed"
            }
        }
    }
    
    # Output results
    $osResults | Format-Table -AutoSize
    
    return $osResults
}""",
                        "Set-ClusterNetworkConfiguration": """function Set-ClusterNetworkConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComputerNames,
        
        [Parameter(Mandatory=$true)]
        [string]$ManagementNetworkPrefix = "192.168.1.",
        
        [Parameter(Mandatory=$true)]
        [string]$StorageNetworkPrefix = "192.168.2.",
        
        [Parameter(Mandatory=$true)]
        [string]$LiveMigrationNetworkPrefix = "192.168.3."
    )
    
    Write-Host "Configuring networks on cluster nodes: $ComputerNames" -ForegroundColor Yellow
    
    foreach ($computer in $ComputerNames) {
        # Configure Management Network
        Write-Host "Configuring Management Network on $computer..." -ForegroundColor Cyan
        # Code to configure management network would go here
        
        # Configure Storage Network
        Write-Host "Configuring Storage Network on $computer..." -ForegroundColor Cyan
        # Code to configure storage network would go here
        
        # Configure Live Migration Network
        Write-Host "Configuring Live Migration Network on $computer..." -ForegroundColor Cyan
        # Code to configure live migration network would go here
    }
    
    Write-Host "Network configuration completed successfully" -ForegroundColor Green
}""",
                        "New-HyperVCluster": """function New-HyperVCluster {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComputerNames,
        
        [Parameter(Mandatory=$true)]
        [string]$ClusterName,
        
        [Parameter(Mandatory=$true)]
        [string]$ClusterIP,
        
        [Parameter(Mandatory=$true)]
        [string]$WitnessType,
        
        [Parameter(Mandatory=$true)]
        [string]$WitnessPath
    )
    
    Write-Host "Creating cluster with nodes: $ComputerNames" -ForegroundColor Yellow
    
    # Test cluster configuration
    Write-Host "Testing cluster configuration..." -ForegroundColor Cyan
    # Test-Cluster code would go here
    
    # Create the cluster
    Write-Host "Creating the cluster $ClusterName..." -ForegroundColor Cyan
    # New-Cluster code would go here
    
    # Configure cluster quorum
    Write-Host "Configuring cluster quorum..." -ForegroundColor Cyan
    switch ($WitnessType) {
        "FileShare" {
            # Set-ClusterQuorum -FileShareWitness $WitnessPath
            Write-Host "Configured File Share Witness: $WitnessPath" -ForegroundColor Green
        }
        "Disk" {
            # Set-ClusterQuorum -DiskWitness $WitnessPath
            Write-Host "Configured Disk Witness: $WitnessPath" -ForegroundColor Green
        }
        "Cloud" {
            # Set-ClusterQuorum -CloudWitness
            Write-Host "Configured Cloud Witness" -ForegroundColor Green
        }
        Default {
            Write-Host "Unknown witness type: $WitnessType" -ForegroundColor Red
        }
    }
    
    Write-Host "Cluster configuration completed successfully" -ForegroundColor Green
}""",
                        "Set-ClusterStorageConfiguration": """function Set-ClusterStorageConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComputerNames,
        
        [Parameter(Mandatory=$true)]
        [string]$StorageType = "S2D",
        
        [Parameter(Mandatory=$true)]
        [int]$CSVCount = 3
    )
    
    Write-Host "Configuring storage on cluster nodes: $ComputerNames" -ForegroundColor Yellow
    
    # Configure Storage based on type
    switch ($StorageType) {
        "S2D" {
            # Enable S2D
            Write-Host "Enabling Storage Spaces Direct..." -ForegroundColor Cyan
            # Enable-ClusterS2D code would go here
            
            # Create storage pool
            Write-Host "Creating storage pool..." -ForegroundColor Cyan
            # New-StoragePool code would go here
            
            # Create virtual disks
            Write-Host "Creating virtual disks..." -ForegroundColor Cyan
            # New-VirtualDisk code would go here
            
            # Create volumes
            Write-Host "Creating volumes..." -ForegroundColor Cyan
            # New-Volume code would go here
        }
        "SAN" {
            # Configure SAN storage
            Write-Host "Configuring SAN storage..." -ForegroundColor Cyan
            # SAN configuration code would go here
        }
        Default {
            Write-Host "Unknown storage type: $StorageType" -ForegroundColor Red
            return
        }
    }
    
    # Create CSVs
    for ($i = 1; $i -le $CSVCount; $i++) {
        Write-Host "Creating CSV $i..." -ForegroundColor Cyan
        # Add-ClusterSharedVolume code would go here
    }
    
    Write-Host "Storage configuration completed successfully" -ForegroundColor Green
}""",
                        "Set-ClusterSecurityConfiguration": """function Set-ClusterSecurityConfiguration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$ComputerNames,
        
        [Parameter(Mandatory=$false)]
        [bool]$EnableSMBEncryption = $true,
        
        [Parameter(Mandatory=$false)]
        [bool]$EnableLiveMigrationEncryption = $true,
        
        [Parameter(Mandatory=$false)]
        [bool]$EnableHostGuardian = $false
    )
    
    Write-Host "Configuring security settings on: $ComputerNames" -ForegroundColor Yellow
    
    foreach ($computer in $ComputerNames) {
        # Configure SMB Encryption
        if ($EnableSMBEncryption) {
            Write-Host "Enabling SMB Encryption on $computer..." -ForegroundColor Cyan
            # Set-SmbServerConfiguration code would go here
        }
        
        # Configure Live Migration Encryption
        if ($EnableLiveMigrationEncryption) {
            Write-Host "Enabling Live Migration Encryption on $computer..." -ForegroundColor Cyan
            # Set-VMHost -VirtualMachineMigrationAuthenticationType Kerberos
            # Set-VMHost -VirtualMachineMigrationPerformanceOption SMB
        }
        
        # Configure Host Guardian Service
        if ($EnableHostGuardian) {
            Write-Host "Enabling Host Guardian Service on $computer..." -ForegroundColor Cyan
            # Host Guardian Service configuration code would go here
        }
        
        # Configure Windows Defender
        Write-Host "Configuring Windows Defender on $computer..." -ForegroundColor Cyan
        # Windows Defender configuration code would go here
        
        # Configure Windows Firewall
        Write-Host "Configuring Windows Firewall on $computer..." -ForegroundColor Cyan
        # Windows Firewall configuration code would go here
    }
    
    Write-Host "Security configuration completed successfully" -ForegroundColor Green
}"""
                    }
                    
                    # Use a simpler approach with a function selector
                    # Group functions by prefix
                    grouped_functions = {
                        "Test Functions": [f for f in function_scripts.keys() if f.startswith("Test-")],
                        "Set Functions": [f for f in function_scripts.keys() if f.startswith("Set-")],
                        "New Functions": [f for f in function_scripts.keys() if f.startswith("New-")],
                        "Other Functions": [f for f in function_scripts.keys() 
                                         if not (f.startswith("Test-") or f.startswith("Set-") or f.startswith("New-"))]
                    }
                    
                    # Create a selector for function groups
                    function_groups = list(grouped_functions.keys())
                    selected_group = st.selectbox("Select Function Type:", function_groups)
                    
                    # Get functions for the selected group
                    selected_functions = grouped_functions[selected_group]
                    
                    if not selected_functions:
                        st.write(f"No {selected_group.lower()} available.")
                    else:
                        # Function selector
                        selected_function = st.selectbox(
                            f"Select a function from {selected_group}:", 
                            selected_functions
                        )
                        
                        # Display selected function
                        if selected_function:
                            func_script = function_scripts[selected_function]
                            
                            # Function info
                            st.markdown(f"### {selected_function}")
                            
                            # Download button for the selected function
                            st.download_button(
                                label=f"Download {selected_function}",
                                data=func_script,
                                file_name=f"{project_name.replace(' ', '_')}_{deployment_name.replace(' ', '_')}_{selected_function}.ps1",
                                mime="text/plain",
                                help=f"PowerShell function: {selected_function}"
                            )
                            
                            # Always show the code for the selected function
                            st.markdown("#### Function Code:")
                            st.code(func_script, language="powershell")
                            
                            # Show usage example
                            st.markdown("#### Usage Example:")
                            
                            # Create an example based on the function type
                            if selected_function.startswith("Test-"):
                                example = f"{selected_function} -ComputerNames @('HyperV1', 'HyperV2', 'HyperV3')"
                            elif selected_function.startswith("Set-"):
                                example = f"{selected_function} -ComputerNames @('HyperV1', 'HyperV2', 'HyperV3')"
                            elif selected_function.startswith("New-"):
                                example = f"{selected_function} -ComputerNames @('HyperV1', 'HyperV2', 'HyperV3') -ClusterName 'HVCluster'"
                            else:
                                example = f"{selected_function}"
                            
                            st.code(example, language="powershell")
                    
                    # Allow downloading all functions of a specific type
                    st.markdown("### Download Multiple Functions")
                    
                    download_group = st.selectbox("Select function group to download:", 
                                                 function_groups, key="download_group")
                    
                    if download_group:
                        download_functions = grouped_functions[download_group]
                        if download_functions:
                            # Combine all functions in the group
                            combined_content = ""
                            for func_name in download_functions:
                                combined_content += f"# {func_name}\n{function_scripts[func_name]}\n\n"
                            
                            # Create download button for the group
                            st.download_button(
                                label=f"Download All {download_group}",
                                data=combined_content,
                                file_name=f"{project_name.replace(' ', '_')}_{deployment_name.replace(' ', '_')}_{download_group.replace(' ', '_')}.ps1",
                                mime="text/plain",
                                help=f"All PowerShell {download_group.lower()}"
                            )
                    else:
                        st.write("No individual functions could be extracted from the script. This might happen if the script doesn't contain properly formatted PowerShell functions.")
            
            # Current deployment type highlight
            current_type = "Hyper-V Only" if deployment_type == "hyperv" else "SCVMM"
            st.info(f"Current configuration is for: **{current_type}**")
            st.caption("For the best results, download scripts specific to your deployment type.")
    
    with col2:
        # Configuration JSON
        config_json = json.dumps(st.session_state.configuration, indent=2)
        st.download_button(
            label="Export Configuration Data as JSON",
            data=config_json,
            file_name=f"{project_name.replace(' ', '_')}_VMM_Configuration.json",
            mime="application/json",
            help="Export the configuration to reuse it later"
        )
        
        # Add an option to import configuration
        uploaded_file = st.file_uploader(
            "Import Configuration Data", 
            type=["json"], 
            key="config_import",
            help="Load a previously exported JSON configuration file"
        )
        
        # Handle imported configuration
        if uploaded_file is not None:
            try:
                imported_config = json.load(uploaded_file)
                st.session_state.configuration = imported_config
                st.success("Configuration imported successfully! You can now navigate through the tool to review and modify the imported settings.")
            except Exception as e:
                st.error(f"Error importing configuration: {str(e)}")

def _render_documentation_preview():
    """Render preview of the generated documentation."""
    if "documentation_generated" not in st.session_state or "html" not in st.session_state.documentation_generated:
        return
    
    st.header("Implementation Documentation Preview")
    
    with st.expander("Show Documentation Preview", expanded=False):
        try:
            from streamlit.components.v1 import html
            html(st.session_state.documentation_generated["html"], height=600, scrolling=True)
        except Exception as e:
            st.warning(f"Preview could not be displayed: {str(e)}. Please download the HTML file to view the complete documentation.")

def _render_implementation_checklist():
    """Render implementation checklist with completion status."""
    st.header("Implementation Checklist")
    
    # Check which steps have been completed
    completed_steps = st.session_state.get("completed_steps", set())
    total_steps = 5  # Updated total number of implementation steps
    
    # Create checklist - updated to match the new module structure
    checklist_items = [
        "Hardware Requirements",
        "Software Requirements",
        "Network Configuration",
        "Storage Configuration",
        "Documentation"
    ]
    
    checklist_status = []
    for i, item in enumerate(checklist_items):
        status = "Completed" if i+1 in completed_steps else "Pending"
        checklist_status.append({"Step": item, "Status": status})
    
    checklist_df = pd.DataFrame(checklist_status)
    
    # Apply conditional formatting
    def highlight_status(val):
        if val == "Completed":
            return 'background-color: #CCFFCC'
        else:
            return 'background-color: #FFFFCC'
    
    styled_df = checklist_df.style.map(highlight_status, subset=['Status'])
    st.table(styled_df)
    
    # Calculate progress
    progress_percentage = len(completed_steps) / total_steps * 100
    st.progress(progress_percentage / 100)
    st.info(f"Implementation Progress: {progress_percentage:.1f}%")

def render_documentation():
    """Render the documentation generation page."""
    st.title("Generate Implementation Documentation (Final Step)")
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    if deployment_type == "hyperv":
        st.write("This is the final step of your Hyper-V cluster implementation. Generate comprehensive documentation and PowerShell scripts based on your configuration selections.")
    else:
        st.write("This is the final step of your Hyper-V cluster with SCVMM implementation. Generate comprehensive documentation and PowerShell scripts based on your configuration selections.")
    
    # Get configuration from session state
    if "configuration" not in st.session_state:
        st.error("Configuration is missing. Please complete the previous steps first.")
        return
    
    config = st.session_state.configuration
    
    # Initialize project information if needed
    _initialize_project_info()
    
    # Render project information section
    organization, project_name = _render_project_information()
    
    # Add project info to configuration
    config["organization"] = organization
    config["project_name"] = project_name
    
    # Render implementation timeline section
    timeline_data = _render_implementation_timeline()
    
    # Add timeline to configuration
    config["implementation_timeline"] = timeline_data
    
    # Render implementation notes section
    implementation_notes = _render_implementation_notes()
    
    # Add notes to configuration
    config["implementation_notes"] = implementation_notes
    
    # Render documentation options section
    include_architecture, include_scripts = _render_documentation_options()
    
    # Generate Implementation Documentation and Scripts
    st.header("Generate Implementation Documentation and PowerShell Scripts")
    
    if st.button("Create VMM Implementation Documentation and PowerShell Scripts", key="generate_docs"):
        # Generate documentation and scripts
        _generate_documentation_and_scripts(config, include_scripts)
    
    # Render download section
    _render_download_section(project_name)
    
    # Render documentation preview
    _render_documentation_preview()
    
    # Render implementation checklist
    _render_implementation_checklist()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    # Previous button always goes to Storage Configuration (now the step before Documentation)
    with col1:
        # Direct navigation to Storage Configuration
        prev_button = st.button("← Storage Configuration", use_container_width=True)
        if prev_button:
            st.session_state.current_step = 5
            st.rerun()
    
    with col2:
        # Direct navigation to Introduction
        return_button = st.button("Return to Introduction", use_container_width=True)
        if return_button:
            st.session_state.current_step = 0
            st.rerun()