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

def render_documentation():
    """Render the documentation generation page."""
    st.title("Documentation Generation")
    
    st.write("Generate comprehensive documentation for your VMM cluster implementation based on your configuration selections.")
    
    # Get configuration from session state
    if "configuration" not in st.session_state:
        st.error("Configuration is missing. Please complete the previous steps first.")
        return
    
    config = st.session_state.configuration
    
    # Project information
    st.header("Project Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        organization = st.text_input(
            "Organization Name",
            value="Example Organization",
            help="Enter your organization name"
        )
    
    with col2:
        project_name = st.text_input(
            "Project Name",
            value="VMM Cluster Implementation",
            help="Enter the project name"
        )
    
    # Add project info to configuration
    config["organization"] = organization
    config["project_name"] = project_name
    
    # Implementation timeline
    st.header("Implementation Timeline")
    
    with st.expander("Implementation Timeline", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Implementation Start Date",
                value=datetime.date.today(),
                help="Select the expected start date for the implementation"
            )
        
        with col2:
            implementation_duration = st.number_input(
                "Implementation Duration (days)",
                min_value=1,
                max_value=30,
                value=7,
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
        
        # Add timeline to configuration
        config["implementation_timeline"] = timeline_data
    
    # Implementation notes
    st.header("Implementation Notes")
    
    implementation_notes = st.text_area(
        "Additional Notes",
        value="",
        height=100,
        help="Enter any additional implementation notes or special requirements"
    )
    
    config["implementation_notes"] = implementation_notes
    
    # Documentation Options
    st.header("Documentation Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_architecture = st.checkbox(
            "Include Architecture Diagrams",
            value=True,
            help="Include network and storage architecture diagrams in the documentation"
        )
    
    with col2:
        include_scripts = st.checkbox(
            "Generate PowerShell Scripts",
            value=True,
            help="Generate PowerShell scripts for implementation tasks"
        )
    
    # Generate Implementation Documentation and Scripts
    st.header("Generate Implementation Documentation and PowerShell Scripts")
    
    if st.button("Create VMM Implementation Documentation and PowerShell Scripts", key="generate_docs"):
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
    
    # Download Documentation and Scripts
    if "documentation_generated" in st.session_state:
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
            if "scripts" in st.session_state.documentation_generated and include_scripts:
                # Create a zip file of scripts
                script_content = ""
                for script_name, script_text in st.session_state.documentation_generated["scripts"].items():
                    script_content += f"# {script_name}\n{script_text}\n\n"
                
                st.download_button(
                    label="PowerShell-Implementierungsskripte herunterladen",
                    data=script_content,
                    file_name=f"{project_name.replace(' ', '_')}_VMM_Implementierungsskripte.ps1",
                    mime="text/plain",
                    help="Ausführbare PowerShell-Skripte für die automatisierte VMM-Implementation"
                )
        
        with col2:
            # Configuration JSON
            config_json = json.dumps(config, indent=2)
            st.download_button(
                label="Konfigurationsdaten als JSON exportieren",
                data=config_json,
                file_name=f"{project_name.replace(' ', '_')}_VMM_Konfiguration.json",
                mime="application/json",
                help="Exportieren Sie die Konfiguration, um sie später wiederverwenden zu können"
            )
            
            # Add an option to import configuration
            st.file_uploader(
                "Konfigurationsdaten importieren", 
                type=["json"], 
                key="config_import",
                help="Laden Sie eine zuvor exportierte JSON-Konfigurationsdatei"
            )
    
    # Vorschau der generierten Dokumentation
    if "documentation_generated" in st.session_state and "html" in st.session_state.documentation_generated:
        st.header("Vorschau der Implementierungsdokumentation")
        
        with st.expander("Dokumentationsvorschau anzeigen", expanded=False):
            try:
                st.components.v1.html(st.session_state.documentation_generated["html"], height=600, scrolling=True)
            except:
                st.warning("Vorschau konnte nicht angezeigt werden. Laden Sie die HTML-Datei herunter, um die vollständige Dokumentation zu sehen.")
    
    # Implementierungs-Checkliste
    st.header("Implementierungs-Checkliste")
    
    # Check which steps have been completed
    completed_steps = st.session_state.get("completed_steps", set())
    total_steps = 10  # Total number of implementation steps
    
    # Create checklist
    checklist_items = [
        "Hardware-Anforderungen",
        "Software-Anforderungen",
        "Netzwerkkonfiguration",
        "Speicherkonfiguration",
        "Sicherheitseinstellungen",
        "Hochverfügbarkeit",
        "Backup & Wiederherstellung",
        "Rollen & Berechtigungen",
        "Monitoring",
        "Dokumentation"
    ]
    
    checklist_status = []
    for i, item in enumerate(checklist_items):
        status = "Abgeschlossen" if i+1 in completed_steps else "Ausstehend"
        checklist_status.append({"Schritt": item, "Status": status})
    
    checklist_df = pd.DataFrame(checklist_status)
    
    # Apply conditional formatting
    def highlight_status(val):
        if val == "Abgeschlossen":
            return 'background-color: #CCFFCC'
        else:
            return 'background-color: #FFFFCC'
    
    styled_df = checklist_df.style.applymap(highlight_status, subset=['Status'])
    st.table(styled_df)
    
    # Calculate progress
    progress_percentage = len(completed_steps) / total_steps * 100
    st.progress(progress_percentage / 100)
    st.info(f"Implementierungsfortschritt: {progress_percentage:.1f}%")
    
    # Diese Bereiche wurden bereits weiter oben implementiert
    # in der Spalte "Konfigurationsdaten als JSON exportieren"
    # und "Konfigurationsdaten importieren"
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: Monitoring", key="prev_monitoring"):
            st.session_state.current_step = 9
            st.rerun()
    
    with col2:
        if st.button("Return to Introduction", key="return_intro"):
            st.session_state.current_step = 0
            st.rerun()
