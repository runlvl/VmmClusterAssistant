import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render_backup_restore():
    """Render the backup and restore configuration page."""
    st.title("Backup & Restore")
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    if deployment_type == "hyperv":
        st.write("Configure backup and restore settings for your Hyper-V cluster. A robust backup strategy is essential for disaster recovery.")
    else:
        st.write("Configure backup and restore settings for your Hyper-V cluster with SCVMM. A robust backup strategy is essential for disaster recovery.")
    
    # Initialize backup configuration in session state if not present
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "backup" not in st.session_state.configuration:
        st.session_state.configuration["backup"] = {
            "vmm_db_method": "SQL Backup",
            "vmm_db_frequency": "Daily",
            "vmm_db_retention": "30 days",
            "library_method": "File Backup",
            "library_frequency": "Weekly",
            "library_retention": "30 days",
            "vm_method": "Hyper-V Backup",
            "vm_frequency": "Daily",
            "vm_retention": "30 days",
            "host_method": "System State Backup",
            "host_frequency": "Weekly",
            "host_retention": "30 days"
        }
    
    # Function to update session state when backup configuration is confirmed
    def confirm_backup_configuration():
        st.session_state.configuration["backup"] = {
            "vmm_db_method": vmm_db_method,
            "vmm_db_frequency": vmm_db_frequency,
            "vmm_db_retention": vmm_db_retention,
            "library_method": library_method,
            "library_frequency": library_frequency,
            "library_retention": library_retention,
            "vm_method": vm_method,
            "vm_frequency": vm_frequency,
            "vm_retention": vm_retention,
            "host_method": host_method,
            "host_frequency": host_frequency,
            "host_retention": host_retention,
            "backup_location": backup_location,
            "encryption_enabled": encryption_enabled,
            "notification_email": notification_email
        }
        
        if "completed_steps" not in st.session_state:
            st.session_state.completed_steps = set()
        
        st.session_state.completed_steps.add(7)  # Mark backup step as completed
        st.session_state.current_step = 8  # Move to next step (roles & permissions)
        st.rerun()
    
    # Get deployment type to determine which sections to show
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    # VMM-specific backup options (only shown for SCVMM deployment)
    if deployment_type == "scvmm":
        # VMM Database Backup
        st.header("VMM Database Backup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            vmm_db_method = st.selectbox(
                "Backup Method",
                options=["SQL Backup", "SQL Always On", "DPM", "Third-party Tool"],
                index=0,
                help="Select the backup method for the VMM database"
            )
        
        with col2:
            vmm_db_frequency = st.selectbox(
                "Backup Frequency",
                options=["Hourly", "Daily", "Weekly"],
                index=1,
                help="Select how often to back up the VMM database"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            vmm_db_retention = st.selectbox(
                "Retention Period",
                options=["7 days", "14 days", "30 days", "60 days", "90 days"],
                index=2,
                help="Select how long to keep VMM database backups"
            )
        
        # VMM Library Backup
        st.header("VMM Library Backup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            library_method = st.selectbox(
                "Backup Method",
                options=["File Backup", "DPM", "Third-party Tool"],
                index=0,
                help="Select the backup method for the VMM library"
            )
    else:
        # For Hyper-V only deployment, set default values but don't show UI
        vmm_db_method = "None"
        vmm_db_frequency = "None"
        vmm_db_retention = "None"
        library_method = "None"
    
    # Library backup options - only shown if SCVMM is selected
    if deployment_type == "scvmm":
        # Create columns inside the if block to avoid unbound variables
        lib_col1, lib_col2 = st.columns(2)
        
        with lib_col2:
            library_frequency = st.selectbox(
                "Backup Frequency",
                options=["Daily", "Weekly", "Monthly"],
                index=1,
                help="Select how often to back up the VMM library"
            )
        
        lib_col3, lib_col4 = st.columns(2)
        
        with lib_col3:
            library_retention = st.selectbox(
                "Retention Period",
                options=["7 days", "14 days", "30 days", "60 days", "90 days"],
                index=2,
                help="Select how long to keep VMM library backups"
            )
    else:
        # For Hyper-V only deployment, set default values but don't show UI
        library_frequency = "None"
        library_retention = "None"
    
    # Virtual Machine Backup
    st.header("Virtual Machine Backup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vm_method = st.selectbox(
            "Backup Method",
            options=["Hyper-V Backup", "DPM", "Azure Backup", "Third-party Tool"],
            index=0,
            help="Select the backup method for virtual machines"
        )
    
    with col2:
        vm_frequency = st.selectbox(
            "Backup Frequency",
            options=["Hourly", "Daily", "Weekly"],
            index=1,
            help="Select how often to back up virtual machines"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        vm_retention = st.selectbox(
            "Retention Period",
            options=["7 days", "14 days", "30 days", "60 days", "90 days"],
            index=2,
            help="Select how long to keep virtual machine backups"
        )
    
    # Host Configuration Backup
    st.header("Host Configuration Backup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        host_method = st.selectbox(
            "Backup Method",
            options=["System State Backup", "DPM", "Third-party Tool"],
            index=0,
            help="Select the backup method for host configurations"
        )
    
    with col2:
        host_frequency = st.selectbox(
            "Backup Frequency",
            options=["Daily", "Weekly", "Monthly"],
            index=1,
            help="Select how often to back up host configurations"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        host_retention = st.selectbox(
            "Retention Period",
            options=["7 days", "14 days", "30 days", "60 days", "90 days"],
            index=2,
            help="Select how long to keep host configuration backups"
        )
    
    # Backup Storage Configuration
    st.header("Backup Storage Configuration")
    
    backup_location = st.selectbox(
        "Backup Storage Location",
        options=["Local Disk", "Network Share", "Azure Storage", "Tape Library"],
        index=1,
        help="Select where to store the backups"
    )
    
    if backup_location == "Network Share":
        backup_share = st.text_input(
            "Network Share Path",
            value="\\\\backupserver\\backups",
            help="Enter the UNC path to the backup share"
        )
    elif backup_location == "Azure Storage":
        azure_storage_account = st.text_input(
            "Azure Storage Account",
            value="",
            help="Enter the Azure storage account name"
        )
    
    encryption_enabled = st.checkbox(
        "Enable Backup Encryption",
        value=True,
        help="Encrypt backup data for enhanced security"
    )
    
    # Backup Notifications
    st.header("Backup Notifications")
    
    notification_email = st.text_input(
        "Notification Email",
        value="admin@example.com",
        help="Email address for backup notifications"
    )
    
    # Recovery Testing Schedule
    st.header("Recovery Testing Schedule")
    
    with st.expander("Recovery Testing Configuration", expanded=False):
        st.write("Schedule regular recovery testing to ensure backups are valid and restorable.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_vms = st.checkbox(
                "Test VM Recovery",
                value=True,
                help="Regularly test VM recovery from backups"
            )
        
        with col2:
            test_db = st.checkbox(
                "Test Database Recovery",
                value=True,
                help="Regularly test VMM database recovery from backups"
            )
        
        test_frequency = st.selectbox(
            "Testing Frequency",
            options=["Monthly", "Quarterly", "Bi-annually", "Annually"],
            index=1,
            help="How often to test recovery procedures"
        )
    
    # Backup visualization
    st.header("Backup Schedule Visualization")
    
    # Create backup schedule data
    backup_data = [
        {"Component": "VMM Database", "Frequency": vmm_db_frequency, "Retention": vmm_db_retention},
        {"Component": "VMM Library", "Frequency": library_frequency, "Retention": library_retention},
        {"Component": "Virtual Machines", "Frequency": vm_frequency, "Retention": vm_retention},
        {"Component": "Host Configuration", "Frequency": host_frequency, "Retention": host_retention}
    ]
    
    # Create DataFrame
    df = pd.DataFrame(backup_data)
    
    # Create frequency color mapping
    freq_color_map = {
        "Hourly": "#2ca02c",  # Green
        "Daily": "#1f77b4",   # Blue
        "Weekly": "#ff7f0e",  # Orange
        "Monthly": "#d62728"  # Red
    }
    
    # Create bar chart for backup schedule
    fig = px.bar(df, x="Component", y=["Frequency"], 
                 title="Backup Frequency by Component",
                 barmode="group",
                 color_discrete_map={"Frequency": "#1f77b4"},
                 height=400)
    
    st.plotly_chart(fig)
    
    # Create retention period chart
    retention_days = {
        "7 days": 7,
        "14 days": 14,
        "30 days": 30,
        "60 days": 60,
        "90 days": 90
    }
    
    df["RetentionDays"] = df["Retention"].map(retention_days)
    
    fig2 = px.bar(df, x="Component", y="RetentionDays", 
                  title="Backup Retention Period (Days)",
                  color="Component",
                  height=400)
    
    st.plotly_chart(fig2)
    
    # Recovery procedures
    st.header("Recovery Procedures")
    
    with st.expander("VMM Server Recovery", expanded=True):
        st.write("""
        ### VMM Server Recovery Procedure
        
        1. **Restore VMM Database**: Restore the VMM database to the SQL Server instance
        2. **Reinstall VMM**: Install VMM on the server
        3. **Use SCVMMRecover.exe**: Run the VMM recovery tool to reconnect to the database
        4. **Verify Connections**: Verify connections to hosts and library servers
        5. **Update Host Configurations**: If needed, update host configurations
        
        For detailed recovery steps, refer to the Microsoft documentation: [Recover VMM](https://docs.microsoft.com/en-us/system-center/vmm/backup-restore-vmm)
        """)
    
    with st.expander("Host Recovery", expanded=False):
        st.write("""
        ### Hyper-V Host Recovery Procedure
        
        1. **Reinstall Operating System**: Reinstall Windows Server on the host
        2. **Install Hyper-V Role**: Install the Hyper-V role
        3. **Add to Cluster**: Add the host back to the Hyper-V cluster
        4. **Add to VMM**: Add the host back to VMM management
        5. **Restore Configuration**: Apply previous configuration settings
        
        For detailed host recovery steps, refer to the Microsoft documentation.
        """)
    
    with st.expander("VM Recovery", expanded=False):
        st.write("""
        ### Virtual Machine Recovery Procedure
        
        1. **Select VM to Restore**: Identify the VM that needs to be restored
        2. **Choose Recovery Point**: Select the appropriate backup point
        3. **Restore VM**: Use the backup software to restore the VM
        4. **Verify VM Settings**: Check VM settings and configurations
        5. **Start VM**: Start the restored VM and verify functionality
        
        For detailed VM recovery steps, refer to your backup solution's documentation.
        """)
    
    # Backup and recovery best practices
    st.header("Backup & Recovery Best Practices")
    
    best_practices = [
        "Regularly test recovery procedures to ensure backups are valid",
        "Store backup media in a secure, off-site location",
        "Maintain documentation of recovery procedures",
        "Automate backup processes where possible",
        "Encrypt backup data for sensitive information",
        "Use the 3-2-1 backup strategy: 3 copies, 2 different media types, 1 offsite",
        "Verify backup integrity automatically after completion",
        "Monitor backup job status and address failures promptly",
        "Regularly review and adjust backup strategies based on changing requirements",
        "Document recovery time and recovery point objectives (RTO/RPO)"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: High Availability", key="prev_ha"):
            st.session_state.current_step = 6
            st.rerun()
    
    with col2:
        st.button("Next: Roles & Permissions", on_click=confirm_backup_configuration)
