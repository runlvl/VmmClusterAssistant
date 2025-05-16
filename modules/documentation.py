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
                
                # 1. Get combined scripts (all and by deployment type)
                # All scripts combined
                all_scripts_content = ""
                hyperv_scripts_content = ""
                scvmm_scripts_content = ""
                
                # Extract scripts and organize them
                for category in scripts:
                    if category == "by_task" and isinstance(scripts[category], dict):
                        # Handle by_task structure separately
                        continue
                    elif isinstance(scripts[category], dict):
                        for script_name, script_text in scripts[category].items():
                            if isinstance(script_text, str):
                                all_scripts_content += f"# {script_name}\n{script_text}\n\n"
                                
                                # Add to Hyper-V scripts if appropriate
                                if category == "common" or category == "hyperv":
                                    hyperv_scripts_content += f"# {script_name}\n{script_text}\n\n"
                                
                                # Add to SCVMM scripts if appropriate
                                if category == "common" or category == "scvmm":
                                    scvmm_scripts_content += f"# {script_name}\n{script_text}\n\n"
                
                # Get script contents by task, for each deployment type
                hyperv_by_task = {}
                scvmm_by_task = {}
                all_by_task = {}
                
                # Define task categories
                task_categories = [
                    ("prerequisites", "Prerequisites"),
                    ("network", "Network Configuration"),
                    ("storage", "Storage Configuration"),
                    ("cluster", "Cluster Configuration"),
                    ("security", "Security Configuration")
                ]
                
                # Extract task-specific scripts
                if "by_task" in scripts and isinstance(scripts["by_task"], dict):
                    for task_key, task_dict in scripts["by_task"].items():
                        if isinstance(task_dict, dict):
                            all_by_task[task_key] = ""
                            hyperv_by_task[task_key] = ""
                            scvmm_by_task[task_key] = ""
                            
                            for script_name, script_text in task_dict.items():
                                if isinstance(script_text, str):
                                    # Add script to 'all' tasks
                                    all_by_task[task_key] += f"# {script_name}\n{script_text}\n\n"
                                    
                                    # Determine if this script is for Hyper-V, SCVMM, or both
                                    if "SCVMM" in script_name or "VMM" in script_name:
                                        scvmm_by_task[task_key] += f"# {script_name}\n{script_text}\n\n"
                                    elif "Hyper-V" in script_name or "HyperV" in script_name:
                                        hyperv_by_task[task_key] += f"# {script_name}\n{script_text}\n\n"
                                    else:
                                        # Common script, add to both
                                        hyperv_by_task[task_key] += f"# {script_name}\n{script_text}\n\n"
                                        scvmm_by_task[task_key] += f"# {script_name}\n{script_text}\n\n"
                
                # 2. Download tabs for different download options
                script_tabs = st.tabs(["Combined Scripts", "Scripts by Deployment Type", "Scripts by Task"])
                
                # Tab 1: Combined Scripts
                with script_tabs[0]:
                    st.download_button(
                        label="Download All PowerShell Scripts (Combined)",
                        data=all_scripts_content,
                        file_name=f"{project_name.replace(' ', '_')}_All_Implementation_Scripts.ps1",
                        mime="text/plain",
                        help="All PowerShell implementation scripts combined in a single file"
                    )
                
                # Tab 2: Scripts by Deployment Type
                with script_tabs[1]:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Hyper-V Only Scripts")
                        st.download_button(
                            label="Download Complete Hyper-V Scripts",
                            data=hyperv_scripts_content,
                            file_name=f"{project_name.replace(' ', '_')}_HyperV_All_Scripts.ps1",
                            mime="text/plain",
                            help="PowerShell scripts for pure Hyper-V cluster implementation"
                        )
                        
                        # Add individual task scripts for Hyper-V
                        for task_key, task_name in task_categories:
                            if task_key in hyperv_by_task and hyperv_by_task[task_key]:
                                st.download_button(
                                    label=f"Hyper-V: {task_name} Script",
                                    data=hyperv_by_task[task_key],
                                    file_name=f"{project_name.replace(' ', '_')}_HyperV_{task_key.capitalize()}.ps1",
                                    mime="text/plain",
                                    help=f"Hyper-V-specific {task_name.lower()} script"
                                )
                    
                    with col2:
                        st.subheader("SCVMM Scripts")
                        st.download_button(
                            label="Download Complete SCVMM Scripts",
                            data=scvmm_scripts_content,
                            file_name=f"{project_name.replace(' ', '_')}_SCVMM_All_Scripts.ps1",
                            mime="text/plain",
                            help="PowerShell scripts for Hyper-V cluster with SCVMM implementation"
                        )
                        
                        # Add individual task scripts for SCVMM
                        for task_key, task_name in task_categories:
                            if task_key in scvmm_by_task and scvmm_by_task[task_key]:
                                st.download_button(
                                    label=f"SCVMM: {task_name} Script",
                                    data=scvmm_by_task[task_key],
                                    file_name=f"{project_name.replace(' ', '_')}_SCVMM_{task_key.capitalize()}.ps1",
                                    mime="text/plain",
                                    help=f"SCVMM-specific {task_name.lower()} script"
                                )
                
                # Tab 3: Scripts by Task with deployment type options
                with script_tabs[2]:
                    # Create a radio button for selecting deployment type
                    deployment_selection = st.radio(
                        "Select Deployment Type for Tasks:",
                        ["All Tasks", "Hyper-V Only Tasks", "SCVMM Tasks"],
                        horizontal=True
                    )
                    
                    # Display task-specific scripts based on selection
                    for task_key, task_name in task_categories:
                        # Skip this task if it doesn't have scripts for the selected deployment type
                        if (deployment_selection == "Hyper-V Only Tasks" and (task_key not in hyperv_by_task or not hyperv_by_task[task_key])) or \
                           (deployment_selection == "SCVMM Tasks" and (task_key not in scvmm_by_task or not scvmm_by_task[task_key])) or \
                           (deployment_selection == "All Tasks" and (task_key not in all_by_task or not all_by_task[task_key])):
                            continue
                            
                        st.markdown(f"#### {task_name}")
                        
                        # Choose the appropriate script content based on selection
                        if deployment_selection == "Hyper-V Only Tasks":
                            task_content = hyperv_by_task[task_key]
                            prefix = "HyperV"
                        elif deployment_selection == "SCVMM Tasks":
                            task_content = scvmm_by_task[task_key]
                            prefix = "SCVMM"
                        else:
                            task_content = all_by_task[task_key]
                            prefix = "All"
                        
                        # Create download button for the task
                        st.download_button(
                            label=f"Download {task_name} Script",
                            data=task_content,
                            file_name=f"{project_name.replace(' ', '_')}_{prefix}_{task_key.capitalize()}.ps1",
                            mime="text/plain",
                            help=f"PowerShell script for {task_name.lower()}"
                        )
                        
                        # Show a preview of the script (first few lines)
                        with st.expander(f"Preview {task_name} Script", expanded=False):
                            lines = task_content.split('\n')
                            preview_lines = '\n'.join(lines[:min(20, len(lines))])
                            if len(lines) > 20:
                                preview_lines += "\n...(more lines)..."
                            st.code(preview_lines, language="powershell")
            
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