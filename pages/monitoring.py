import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render_monitoring():
    """Render the monitoring configuration page."""
    st.title("Monitoring")
    
    st.write("Configure monitoring settings for your VMM cluster. Proper monitoring is essential for maintaining system health and performance.")
    
    # Initialize monitoring configuration in session state if not present
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "monitoring" not in st.session_state.configuration:
        st.session_state.configuration["monitoring"] = {
            "vmm_method": "System Center Operations Manager",
            "cluster_method": "System Center Operations Manager",
            "host_method": "System Center Operations Manager",
            "storage_method": "System Center Operations Manager",
            "network_method": "System Center Operations Manager",
            "notifications": {
                "email": True,
                "sms": False,
                "snmp": False,
                "recipients": "admin@example.com"
            }
        }
    
    # Function to update session state when monitoring configuration is confirmed
    def confirm_monitoring_configuration():
        st.session_state.configuration["monitoring"] = {
            "vmm_method": vmm_method,
            "cluster_method": cluster_method,
            "host_method": host_method,
            "storage_method": storage_method,
            "network_method": network_method,
            "thresholds": {
                "cpu": cpu_threshold,
                "memory": memory_threshold,
                "disk_space": disk_space_threshold,
                "disk_latency": disk_latency_threshold
            },
            "notifications": {
                "email": email_notifications,
                "sms": sms_notifications,
                "snmp": snmp_notifications,
                "recipients": notification_recipients
            },
            "dashboard": dashboard_enabled,
            "reports": reports_enabled,
            "alert_levels": alert_levels
        }
        
        if "completed_steps" not in st.session_state:
            st.session_state.completed_steps = set()
        
        st.session_state.completed_steps.add(9)  # Mark monitoring step as completed
        st.session_state.current_step = 10  # Move to next step (documentation)
        st.rerun()
    
    # Monitoring Methods
    st.header("Monitoring Methods")
    
    # Components to monitor
    components = [
        {"name": "VMM Service", "var_name": "vmm_method"},
        {"name": "Failover Cluster", "var_name": "cluster_method"},
        {"name": "Hyper-V Hosts", "var_name": "host_method"},
        {"name": "Storage", "var_name": "storage_method"},
        {"name": "Network", "var_name": "network_method"}
    ]
    
    # Monitoring methods for each component
    monitoring_methods = {}
    for component in components:
        monitoring_methods[component["var_name"]] = st.selectbox(
            f"{component['name']} Monitoring Method",
            options=["System Center Operations Manager", "Windows Admin Center", "Azure Monitor", "PowerShell Scripts", "Third-party Tool"],
            index=0,
            key=f"method_{component['var_name']}",
            help=f"Select the monitoring method for {component['name']}"
        )
    
    # Extract monitoring methods for each component
    vmm_method = monitoring_methods["vmm_method"]
    cluster_method = monitoring_methods["cluster_method"]
    host_method = monitoring_methods["host_method"]
    storage_method = monitoring_methods["storage_method"]
    network_method = monitoring_methods["network_method"]
    
    # Alert Thresholds
    st.header("Alert Thresholds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cpu_threshold = st.slider(
            "CPU Utilization Alert Threshold (%)",
            min_value=50,
            max_value=100,
            value=80,
            help="Alert when CPU utilization exceeds this percentage"
        )
        
        memory_threshold = st.slider(
            "Memory Utilization Alert Threshold (%)",
            min_value=50,
            max_value=100,
            value=90,
            help="Alert when memory utilization exceeds this percentage"
        )
    
    with col2:
        disk_space_threshold = st.slider(
            "Disk Space Alert Threshold (% free)",
            min_value=5,
            max_value=30,
            value=10,
            help="Alert when free disk space falls below this percentage"
        )
        
        disk_latency_threshold = st.slider(
            "Disk Latency Alert Threshold (ms)",
            min_value=5,
            max_value=50,
            value=20,
            help="Alert when disk latency exceeds this value in milliseconds"
        )
    
    # Alert Levels
    st.subheader("Alert Severity Levels")
    
    with st.expander("Alert Level Configuration", expanded=False):
        st.write("Configure severity levels for different types of alerts.")
        
        alert_types = [
            "VMM Service Down",
            "Host Not Responding",
            "Cluster Node Down",
            "Low Disk Space",
            "High CPU Usage",
            "High Memory Usage",
            "Network Latency",
            "Backup Failure"
        ]
        
        alert_levels = {}
        
        for alert in alert_types:
            alert_levels[alert] = st.selectbox(
                f"{alert} Severity",
                options=["Critical", "Warning", "Information"],
                index=0 if "Down" in alert or "Failure" in alert else 1,
                key=f"severity_{alert.replace(' ', '_')}"
            )
    
    # Notifications
    st.header("Notifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_notifications = st.checkbox(
            "Email Notifications",
            value=True,
            help="Send alert notifications via email"
        )
        
        sms_notifications = st.checkbox(
            "SMS Notifications",
            value=False,
            help="Send alert notifications via SMS"
        )
    
    with col2:
        snmp_notifications = st.checkbox(
            "SNMP Traps",
            value=False,
            help="Send SNMP traps to a management system"
        )
    
    notification_recipients = st.text_input(
        "Notification Recipients",
        value="admin@example.com",
        help="Email addresses or phone numbers for notifications (comma-separated)"
    )
    
    # Dashboard and Reports
    st.header("Dashboard and Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dashboard_enabled = st.checkbox(
            "Enable Monitoring Dashboard",
            value=True,
            help="Create a real-time monitoring dashboard"
        )
    
    with col2:
        reports_enabled = st.checkbox(
            "Enable Scheduled Reports",
            value=True,
            help="Generate and distribute regular performance reports"
        )
    
    if reports_enabled:
        report_frequency = st.selectbox(
            "Report Frequency",
            options=["Daily", "Weekly", "Monthly"],
            index=1,
            help="How often to generate and send reports"
        )
        
        report_recipients = st.text_input(
            "Report Recipients",
            value=notification_recipients,
            help="Email addresses for receiving reports (comma-separated)"
        )
    
    # Monitoring visualization
    st.header("Monitoring Threshold Visualization")
    
    # Create threshold visualization
    thresholds = {
        "Metric": ["CPU Utilization", "Memory Utilization", "Free Disk Space", "Disk Latency"],
        "Value": [cpu_threshold, memory_threshold, disk_space_threshold, disk_latency_threshold],
        "Unit": ["%", "%", "% free", "ms"]
    }
    
    df = pd.DataFrame(thresholds)
    df["Display"] = df["Value"].astype(str) + " " + df["Unit"]
    
    fig = px.bar(df, x="Metric", y="Value", 
                 text="Display",
                 title="Alert Thresholds",
                 height=400)
    
    # Add threshold lines
    for i, metric in enumerate(df["Metric"]):
        if metric == "Free Disk Space":
            # For disk space, low values are bad
            fig.add_shape(
                type="line",
                x0=i-0.4, x1=i+0.4,
                y0=20, y1=20,
                line=dict(color="yellow", width=3, dash="dash"),
            )
            fig.add_shape(
                type="line",
                x0=i-0.4, x1=i+0.4,
                y0=10, y1=10,
                line=dict(color="red", width=3, dash="dash"),
            )
        else:
            # For other metrics, high values are bad
            if metric == "CPU Utilization":
                fig.add_shape(
                    type="line",
                    x0=i-0.4, x1=i+0.4,
                    y0=70, y1=70,
                    line=dict(color="yellow", width=3, dash="dash"),
                )
                fig.add_shape(
                    type="line",
                    x0=i-0.4, x1=i+0.4,
                    y0=90, y1=90,
                    line=dict(color="red", width=3, dash="dash"),
                )
            elif metric == "Memory Utilization":
                fig.add_shape(
                    type="line",
                    x0=i-0.4, x1=i+0.4,
                    y0=80, y1=80,
                    line=dict(color="yellow", width=3, dash="dash"),
                )
                fig.add_shape(
                    type="line",
                    x0=i-0.4, x1=i+0.4,
                    y0=95, y1=95,
                    line=dict(color="red", width=3, dash="dash"),
                )
            elif metric == "Disk Latency":
                fig.add_shape(
                    type="line",
                    x0=i-0.4, x1=i+0.4,
                    y0=15, y1=15,
                    line=dict(color="yellow", width=3, dash="dash"),
                )
                fig.add_shape(
                    type="line",
                    x0=i-0.4, x1=i+0.4,
                    y0=30, y1=30,
                    line=dict(color="red", width=3, dash="dash"),
                )
    
    st.plotly_chart(fig)
    
    # Monitoring Components Visualization
    st.subheader("Monitoring Component Configuration")
    
    # Create a visualization showing what's being monitored and how
    monitoring_data = []
    for component in components:
        monitoring_data.append({
            "Component": component["name"],
            "Method": monitoring_methods[component["var_name"]],
            "Color": "#1f77b4" if "Operations Manager" in monitoring_methods[component["var_name"]] else 
                     "#ff7f0e" if "Admin Center" in monitoring_methods[component["var_name"]] else
                     "#2ca02c" if "Azure" in monitoring_methods[component["var_name"]] else
                     "#d62728"
        })
    
    monitoring_df = pd.DataFrame(monitoring_data)
    
    fig2 = px.bar(monitoring_df, x="Component", y=[1] * len(monitoring_df),
                  color="Method",
                  title="Monitoring Configuration by Component",
                  height=400)
    
    fig2.update_layout(
        yaxis_visible=False,
        yaxis_showticklabels=False
    )
    
    st.plotly_chart(fig2)
    
    # Sample Dashboard
    st.header("Sample Monitoring Dashboard")
    
    with st.expander("Preview Dashboard", expanded=False):
        # Create a sample dashboard layout
        st.subheader("VMM Cluster Health Dashboard")
        
        # Health status indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="VMM Service", value="Healthy", delta="0 issues")
        
        with col2:
            st.metric(label="Cluster Status", value="Healthy", delta="0 issues")
        
        with col3:
            st.metric(label="Hosts Online", value=f"{node_count}/{node_count}", delta="All online")
        
        with col4:
            st.metric(label="Overall Health", value="Good", delta="100%")
        
        # Sample CPU chart
        cpu_data = {
            "Time": ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"],
            "Host1": [30, 45, 50, 65, 70, 60, 50, 40],
            "Host2": [35, 50, 55, 70, 75, 65, 55, 45]
        }
        
        cpu_df = pd.DataFrame(cpu_data)
        
        fig_cpu = px.line(cpu_df, x="Time", y=["Host1", "Host2"],
                          title="CPU Utilization (%)",
                          height=300)
        
        # Add threshold line
        fig_cpu.add_shape(
            type="line",
            x0=0, x1=7,
            y0=cpu_threshold, y1=cpu_threshold,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        st.plotly_chart(fig_cpu)
        
        # Sample memory chart
        memory_data = {
            "Time": ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"],
            "Host1": [50, 55, 60, 70, 75, 70, 65, 60],
            "Host2": [55, 60, 65, 75, 80, 75, 70, 65]
        }
        
        memory_df = pd.DataFrame(memory_data)
        
        fig_memory = px.line(memory_df, x="Time", y=["Host1", "Host2"],
                             title="Memory Utilization (%)",
                             height=300)
        
        # Add threshold line
        fig_memory.add_shape(
            type="line",
            x0=0, x1=7,
            y0=memory_threshold, y1=memory_threshold,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        st.plotly_chart(fig_memory)
        
        # Sample alerts table
        st.subheader("Recent Alerts")
        
        alerts_data = [
            {"Time": "15:42", "Component": "Host1", "Alert": "High CPU Usage", "Severity": "Warning"},
            {"Time": "14:15", "Component": "Storage", "Alert": "Disk Latency Increase", "Severity": "Information"},
            {"Time": "10:30", "Component": "VM3", "Alert": "Memory Pressure", "Severity": "Warning"},
            {"Time": "Yesterday", "Component": "Backup", "Alert": "Completed Successfully", "Severity": "Information"}
        ]
        
        alerts_df = pd.DataFrame(alerts_data)
        st.table(alerts_df)
    
    # Monitoring best practices
    st.header("Monitoring Best Practices")
    
    best_practices = [
        "Establish baseline performance metrics",
        "Configure appropriate alert thresholds",
        "Set up automated responses for common issues",
        "Implement a tiered alert notification system",
        "Regularly review and tune monitoring settings",
        "Document troubleshooting procedures for common alerts",
        "Use trending and forecasting to predict capacity needs",
        "Monitor both physical and virtual infrastructure",
        "Create dashboards for different stakeholders",
        "Implement automated remediation where possible"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: Roles & Permissions", key="prev_roles"):
            st.session_state.current_step = 8
            st.rerun()
    
    with col2:
        st.button("Next: Documentation", on_click=confirm_monitoring_configuration)
