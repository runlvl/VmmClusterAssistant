import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
import datetime
from utils.documentation_generator import (
    generate_implementation_documentation,
    generate_powershell_scripts,
    export_documentation_to_file,
    export_scripts_to_files
)

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
    
    st.header("Download VMM Implementation Files")
    
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
                
                # 1. Combined script file (all scripts)
                all_scripts_content = ""
                for category in scripts:
                    if isinstance(scripts[category], dict):
                        for script_name, script_text in scripts[category].items():
                            if isinstance(script_text, str):  # Make sure it's a string
                                all_scripts_content += f"# {script_name}\n{script_text}\n\n"
                
                st.download_button(
                    label="Download All PowerShell Scripts (Combined)",
                    data=all_scripts_content,
                    file_name=f"{project_name.replace(' ', '_')}_All_Implementation_Scripts.ps1",
                    mime="text/plain",
                    help="All PowerShell implementation scripts combined in a single file"
                )
                
                st.markdown("---")
                
                # 2. Scripts by Deployment Type
                col1, col2 = st.columns(2)
                
                with col1:
                    # Hyper-V only scripts
                    hyperv_scripts_content = ""
                    
                    # Add common scripts first
                    if "common" in scripts and isinstance(scripts["common"], dict):
                        for script_name, script_text in scripts["common"].items():
                            if isinstance(script_text, str):
                                hyperv_scripts_content += f"# {script_name}\n{script_text}\n\n"
                    
                    # Add Hyper-V specific scripts
                    if "hyperv" in scripts and isinstance(scripts["hyperv"], dict):
                        for script_name, script_text in scripts["hyperv"].items():
                            if isinstance(script_text, str):
                                hyperv_scripts_content += f"# {script_name}\n{script_text}\n\n"
                    
                    st.download_button(
                        label="Download Hyper-V Only Scripts",
                        data=hyperv_scripts_content,
                        file_name=f"{project_name.replace(' ', '_')}_HyperV_Scripts.ps1",
                        mime="text/plain",
                        help="PowerShell scripts for pure Hyper-V cluster implementation"
                    )
                
                with col2:
                    # SCVMM scripts
                    scvmm_scripts_content = ""
                    
                    # Add common scripts first
                    if "common" in scripts and isinstance(scripts["common"], dict):
                        for script_name, script_text in scripts["common"].items():
                            if isinstance(script_text, str):
                                scvmm_scripts_content += f"# {script_name}\n{script_text}\n\n"
                    
                    # Add SCVMM specific scripts
                    if "scvmm" in scripts and isinstance(scripts["scvmm"], dict):
                        for script_name, script_text in scripts["scvmm"].items():
                            if isinstance(script_text, str):
                                scvmm_scripts_content += f"# {script_name}\n{script_text}\n\n"
                    
                    st.download_button(
                        label="Download SCVMM Scripts",
                        data=scvmm_scripts_content,
                        file_name=f"{project_name.replace(' ', '_')}_SCVMM_Scripts.ps1",
                        mime="text/plain",
                        help="PowerShell scripts for Hyper-V cluster with SCVMM implementation"
                    )
                
                st.markdown("---")
                
                # 3. Scripts by Task Category
                st.subheader("Download Scripts by Task Category")
                task_cols = st.columns(3)
                
                # Define task categories
                task_categories = [
                    ("prerequisites", "Prerequisites"),
                    ("network", "Network Configuration"),
                    ("storage", "Storage Configuration"),
                    ("cluster", "Cluster Configuration"),
                    ("security", "Security Configuration")
                ]
                
                # Create download buttons for each task category
                for i, (task_key, task_name) in enumerate(task_categories):
                    col_index = i % 3
                    
                    with task_cols[col_index]:
                        task_content = ""
                        
                        if "by_task" in scripts and task_key in scripts["by_task"] and isinstance(scripts["by_task"][task_key], dict):
                            for script_name, script_text in scripts["by_task"][task_key].items():
                                if isinstance(script_text, str):
                                    task_content += f"# {script_name}\n{script_text}\n\n"
                        
                        if task_content:
                            st.download_button(
                                label=f"Download {task_name} Scripts",
                                data=task_content,
                                file_name=f"{project_name.replace(' ', '_')}_{task_key.capitalize()}_Scripts.ps1",
                                mime="text/plain",
                                help=f"PowerShell scripts for {task_name.lower()}"
                            )
                        else:
                            # If no scripts found for this category, show disabled button
                            st.write(f"{task_name} Scripts (None available)")
            
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
    total_steps = 10  # Total number of implementation steps
    
    # Create checklist
    checklist_items = [
        "Hardware Requirements",
        "Software Requirements",
        "Network Configuration",
        "Storage Configuration",
        "Security Settings",
        "High Availability",
        "Backup & Recovery",
        "Roles & Permissions",
        "Monitoring",
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
    
    # Previous button goes to the previous step, which depends on deployment type
    prev_step_text = "Previous: High Availability" if deployment_type == "hyperv" else "Previous: Monitoring"
    prev_step_key = "prev_ha" if deployment_type == "hyperv" else "prev_monitoring"
    prev_step_num = 7 if deployment_type == "hyperv" else 10
    
    with col1:
        if st.button(prev_step_text, key=prev_step_key):
            st.session_state.current_step = prev_step_num
            st.rerun()
    
    with col2:
        if st.button("Return to Introduction", key="return_intro"):
            st.session_state.current_step = 0
            st.rerun()