import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render_roles_permissions():
    """Render the roles and permissions configuration page."""
    st.title("Roles & Permissions")
    
    st.write("Configure roles and permissions for your VMM cluster. Proper RBAC implementation is essential for secure and efficient management.")
    
    # Initialize roles configuration in session state if not present
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "roles" not in st.session_state.configuration:
        st.session_state.configuration["roles"] = {
            "standard_roles": [
                {
                    "name": "Administrator",
                    "description": "Full control over VMM environment",
                    "permissions": "All permissions"
                },
                {
                    "name": "Fabric Administrator",
                    "description": "Manages physical infrastructure",
                    "permissions": "Host, network, and storage management"
                },
                {
                    "name": "VM Administrator",
                    "description": "Manages virtual machines",
                    "permissions": "Create, modify, and delete VMs"
                },
                {
                    "name": "Read-Only Administrator",
                    "description": "Views but cannot modify environment",
                    "permissions": "View-only access to all components"
                }
            ],
            "custom_roles": [],
            "service_accounts": []
        }
    
    # Function to update session state when roles configuration is confirmed
    def confirm_roles_configuration():
        st.session_state.configuration["roles"] = {
            "standard_roles": standard_roles,
            "custom_roles": custom_roles,
            "service_accounts": service_accounts,
            "self_service": self_service_enabled,
            "self_service_quota": quota_enabled,
            "quota_settings": quota_settings
        }
        
        if "completed_steps" not in st.session_state:
            st.session_state.completed_steps = set()
        
        st.session_state.completed_steps.add(8)  # Mark roles step as completed
        st.session_state.current_step = 9  # Move to next step (monitoring)
        st.rerun()
    
    # Standard Roles
    st.header("Standard Administrator Roles")
    
    # Define standard roles
    standard_roles = [
        {
            "name": "Administrator",
            "description": "Full control over VMM environment",
            "permissions": "All permissions",
            "assigned_users": st.text_input("Administrator Users", value="DOMAIN\\VMM_Admins")
        },
        {
            "name": "Fabric Administrator",
            "description": "Manages physical infrastructure",
            "permissions": "Host, network, and storage management",
            "assigned_users": st.text_input("Fabric Administrator Users", value="DOMAIN\\VMM_Fabric_Admins")
        },
        {
            "name": "VM Administrator",
            "description": "Manages virtual machines",
            "permissions": "Create, modify, and delete VMs",
            "assigned_users": st.text_input("VM Administrator Users", value="DOMAIN\\VMM_VM_Admins")
        },
        {
            "name": "Read-Only Administrator",
            "description": "Views but cannot modify environment",
            "permissions": "View-only access to all components",
            "assigned_users": st.text_input("Read-Only Administrator Users", value="DOMAIN\\VMM_Readers")
        }
    ]
    
    # Display standard roles in a table
    standard_roles_df = pd.DataFrame([
        {
            "Role": role["name"],
            "Description": role["description"],
            "Permissions": role["permissions"],
            "Assigned Users": role["assigned_users"]
        }
        for role in standard_roles
    ])
    
    st.table(standard_roles_df)
    
    # Custom Roles
    st.header("Custom Roles")
    
    add_custom_roles = st.checkbox("Add custom roles", value=False)
    
    custom_roles = []
    
    if add_custom_roles:
        num_custom_roles = st.number_input(
            "Number of custom roles",
            min_value=1,
            max_value=5,
            value=1
        )
        
        for i in range(num_custom_roles):
            with st.expander(f"Custom Role {i+1}"):
                role_name = st.text_input(
                    "Role Name",
                    value=f"Custom Role {i+1}",
                    key=f"role_name_{i}"
                )
                
                role_desc = st.text_input(
                    "Description",
                    value="",
                    key=f"role_desc_{i}"
                )
                
                role_perms_options = [
                    "VM Creation",
                    "VM Modification",
                    "VM Deletion",
                    "Library Access",
                    "Template Creation",
                    "Template Use",
                    "Network Management",
                    "Storage Management",
                    "Host Management",
                    "Reporting"
                ]
                
                role_perms = st.multiselect(
                    "Permissions",
                    options=role_perms_options,
                    default=["VM Creation", "VM Modification"],
                    key=f"role_perms_{i}"
                )
                
                role_users = st.text_input(
                    "Assigned Users",
                    value=f"DOMAIN\\Custom_Role_{i+1}",
                    key=f"role_users_{i}"
                )
                
                # Add to custom roles
                custom_roles.append({
                    "name": role_name,
                    "description": role_desc,
                    "permissions": ", ".join(role_perms),
                    "assigned_users": role_users
                })
    
    # Service Accounts
    st.header("Service Accounts")
    
    # VMM Service Account (from software configuration)
    vmm_account = "DOMAIN\\svc_vmm"
    if "software" in st.session_state.configuration and "service_account" in st.session_state.configuration["software"]:
        vmm_account = st.session_state.configuration["software"]["service_account"]
    
    service_accounts = [
        {
            "name": vmm_account,
            "purpose": "VMM Service Account",
            "permissions": "Local Administrator on VMM servers, SQL Server access"
        }
    ]
    
    with st.expander("Service Accounts Configuration", expanded=False):
        st.write("Configure service accounts for different operations.")
        
        st.info(f"VMM Service Account: {vmm_account}")
        
        additional_accounts = st.number_input(
            "Number of additional service accounts",
            min_value=0,
            max_value=5,
            value=2
        )
        
        # Define default service accounts
        default_accounts = [
            {
                "name": "DOMAIN\\svc_vmm_host",
                "purpose": "Host Management Account",
                "permissions": "Local Administrator on Hyper-V hosts"
            },
            {
                "name": "DOMAIN\\svc_vmm_runas",
                "purpose": "Run As Account",
                "permissions": "Perform operations on behalf of VMM"
            }
        ]
        
        # Use default accounts as starting point
        for i in range(min(additional_accounts, len(default_accounts))):
            col1, col2 = st.columns(2)
            
            with col1:
                account_name = st.text_input(
                    "Account Name",
                    value=default_accounts[i]["name"],
                    key=f"account_name_{i}"
                )
                
                account_purpose = st.text_input(
                    "Purpose",
                    value=default_accounts[i]["purpose"],
                    key=f"account_purpose_{i}"
                )
            
            with col2:
                account_permissions = st.text_area(
                    "Required Permissions",
                    value=default_accounts[i]["permissions"],
                    key=f"account_permissions_{i}",
                    height=100
                )
            
            # Add to service accounts
            service_accounts.append({
                "name": account_name,
                "purpose": account_purpose,
                "permissions": account_permissions
            })
        
        # Add additional accounts if needed
        for i in range(len(default_accounts), additional_accounts):
            col1, col2 = st.columns(2)
            
            with col1:
                account_name = st.text_input(
                    "Account Name",
                    value=f"DOMAIN\\svc_vmm_custom_{i+1}",
                    key=f"account_name_{i}"
                )
                
                account_purpose = st.text_input(
                    "Purpose",
                    value=f"Custom Service Account {i+1}",
                    key=f"account_purpose_{i}"
                )
            
            with col2:
                account_permissions = st.text_area(
                    "Required Permissions",
                    value="",
                    key=f"account_permissions_{i}",
                    height=100
                )
            
            # Add to service accounts
            service_accounts.append({
                "name": account_name,
                "purpose": account_purpose,
                "permissions": account_permissions
            })
    
    # Self-Service Portal
    st.header("Self-Service Portal")
    
    self_service_enabled = st.checkbox(
        "Enable Self-Service Portal",
        value=False,
        help="Allow users to provision their own VMs within defined quotas"
    )
    
    quota_enabled = False
    quota_settings = {}
    
    if self_service_enabled:
        st.subheader("Self-Service Configuration")
        
        quota_enabled = st.checkbox(
            "Enable Resource Quotas",
            value=True,
            help="Set limits on resources that users can provision"
        )
        
        if quota_enabled:
            with st.expander("Quota Settings", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    max_vms = st.number_input(
                        "Maximum VMs per User",
                        min_value=1,
                        value=5
                    )
                    
                    max_vcpus = st.number_input(
                        "Maximum vCPUs per User",
                        min_value=1,
                        value=16
                    )
                
                with col2:
                    max_memory = st.number_input(
                        "Maximum Memory (GB) per User",
                        min_value=1,
                        value=32
                    )
                    
                    max_storage = st.number_input(
                        "Maximum Storage (GB) per User",
                        min_value=10,
                        value=500
                    )
                
                quota_settings = {
                    "max_vms": max_vms,
                    "max_vcpus": max_vcpus,
                    "max_memory_gb": max_memory,
                    "max_storage_gb": max_storage
                }
                
                # Create quota visualization
                quota_values = [max_vms, max_vcpus, max_memory, max_storage]
                quota_labels = ["Max VMs", "Max vCPUs", "Max Memory (GB)", "Max Storage (GB)"]
                
                # Normalize values for visualization
                normalized_values = [
                    max_vms / 10 * 100,
                    max_vcpus / 50 * 100,
                    max_memory / 100 * 100,
                    max_storage / 1000 * 100
                ]
                
                fig = px.bar(
                    x=quota_labels,
                    y=quota_values,
                    title="User Resource Quotas",
                    labels={"x": "Resource Type", "y": "Quota Value"},
                    height=400
                )
                
                st.plotly_chart(fig)
    
    # Role visualization
    st.header("Role Hierarchy Visualization")
    
    # Combine standard and custom roles
    all_roles = standard_roles + custom_roles
    
    # Create a tree-like hierarchy for visualization
    fig = go.Figure()
    
    # Create nodes for each role
    nodes = []
    links = []
    
    # Add VMM system as the root
    nodes.append({
        "id": "VMM",
        "label": "VMM System",
        "level": 0,
        "color": "#1f77b4"
    })
    
    # Add roles as children of VMM
    for i, role in enumerate(all_roles):
        nodes.append({
            "id": role["name"],
            "label": role["name"],
            "level": 1,
            "color": "#ff7f0e" if i < len(standard_roles) else "#2ca02c"
        })
        links.append({"source": "VMM", "target": role["name"]})
    
    # Add service accounts at level 2
    for account in service_accounts:
        nodes.append({
            "id": account["name"],
            "label": account["name"],
            "level": 2,
            "color": "#d62728"
        })
        # Link to Administrator role
        links.append({"source": "Administrator", "target": account["name"]})
    
    # Create positions for nodes
    positions = {}
    
    # Position VMM at the top
    positions["VMM"] = [0, 0]
    
    # Position roles in a row
    role_count = len(all_roles)
    for i, role in enumerate(all_roles):
        x_pos = (i - (role_count - 1) / 2) * 2
        positions[role["name"]] = [x_pos, -2]
    
    # Position service accounts in a row at the bottom
    account_count = len(service_accounts)
    for i, account in enumerate(service_accounts):
        x_pos = (i - (account_count - 1) / 2) * 2
        positions[account["name"]] = [x_pos, -4]
    
    # Create edge traces
    edge_x = []
    edge_y = []
    for link in links:
        x0, y0 = positions[link["source"]]
        x1, y1 = positions[link["target"]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create node traces for each level
    for level in range(3):
        level_nodes = [node for node in nodes if node["level"] == level]
        
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in level_nodes:
            x, y = positions[node["id"]]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node["label"])
            node_color.append(node["color"])
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="bottom center",
            hoverinfo='text',
            marker=dict(
                color=node_color,
                size=20,
                line_width=2))
        
        fig.add_trace(node_trace)
    
    fig.add_trace(edge_trace)
    
    fig.update_layout(
        title="VMM Role Hierarchy",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig)
    
    # Role-based access control best practices
    st.header("Role-Based Access Control Best Practices")
    
    best_practices = [
        "Implement role-based access control for all users",
        "Follow the principle of least privilege",
        "Regularly review and audit user access",
        "Use dedicated service accounts for automated processes",
        "Document all custom roles and their purposes",
        "Limit the number of administrator accounts",
        "Regularly rotate service account passwords",
        "Use groups rather than individual users when assigning roles",
        "Implement a formal process for access requests and approvals",
        "Regularly audit role assignments and permissions"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Previous: Backup & Restore", key="prev_backup"):
            st.session_state.current_step = 7
            st.rerun()
    
    with col2:
        st.button("Next: Monitoring", on_click=confirm_roles_configuration)
