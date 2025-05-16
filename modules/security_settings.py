import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.security_validator import (
    validate_security_configuration,
    validate_admin_account,
    create_security_visualization,
    generate_security_recommendations
)

# Helper functions for security settings

def _initialize_security_config():
    """Initialize security configuration in session state if not present."""
    if "configuration" not in st.session_state:
        st.session_state.configuration = {}
    
    if "security" not in st.session_state.configuration:
        st.session_state.configuration["security"] = {
            "host_hardening": True,
            "network_isolation": True,
            "ipsec_migration": False,
            "smb_encryption": True,
            "dkm": True,
            "roles": []
        }

def _save_security_configuration(host_hardening, network_isolation, ipsec_migration,
                               smb_encryption, dkm_enabled, code_integrity, update_policy,
                               password_policy, roles, dkm_container):
    """Save security configuration to session state."""
    st.session_state.configuration["security"] = {
        "host_hardening": host_hardening,
        "network_isolation": network_isolation,
        "ipsec_migration": ipsec_migration,
        "smb_encryption": smb_encryption,
        "dkm": dkm_enabled,
        "code_integrity": code_integrity,
        "update_policy": update_policy,
        "password_policy": password_policy,
        "roles": roles,
        "dkm_container": dkm_container
    }
    
    if "completed_steps" not in st.session_state:
        st.session_state.completed_steps = set()
    
    st.session_state.completed_steps.add(5)  # Mark security step as completed
    st.session_state.current_step = 7  # Move to next step (documentation)
    st.rerun()

def _render_host_security():
    """Render host security configuration options."""
    st.header("Host Security")
    
    host_hardening = st.checkbox(
        "Enable Host Hardening",
        value=True,
        help="Use minimal Windows Server installation and security best practices"
    )
    
    code_integrity = st.checkbox(
        "Enable Code Integrity Policies",
        value=False,
        help="Prevent unauthorized code execution on Hyper-V hosts"
    )
    
    update_policy = st.checkbox(
        "Establish Update Policy",
        value=True,
        help="Regularly apply security updates to all components"
    )
    
    return host_hardening, code_integrity, update_policy

def _render_network_security():
    """Render network security configuration options."""
    st.header("Network Security")
    
    network_isolation = st.checkbox(
        "Enable Network Isolation",
        value=True,
        help="Use separate networks for different traffic types"
    )
    
    ipsec_migration = st.checkbox(
        "Enable IPsec for Live Migration",
        value=False,
        help="Encrypt live migration traffic for enhanced security"
    )
    
    # If network configuration set IPsec already, use that value
    if "network" in st.session_state.configuration and "ipsec" in st.session_state.configuration["network"]:
        ipsec_migration = st.session_state.configuration["network"]["ipsec"]
    
    return network_isolation, ipsec_migration

def _render_data_security():
    """Render data security configuration options."""
    st.header("Data Security")
    
    smb_encryption = st.checkbox(
        "Enable SMB Encryption",
        value=True,
        help="Use SMB 3.0 encryption for file shares"
    )
    
    dkm_enabled = st.checkbox(
        "Enable Distributed Key Management (DKM)",
        value=True,
        help="Store encryption keys securely in Active Directory"
    )
    
    if dkm_enabled:
        # Get DKM container from software settings if available
        default_container = "VMM_DKM"
        if "software" in st.session_state.configuration and "dkm_container" in st.session_state.configuration["software"]:
            default_container = st.session_state.configuration["software"]["dkm_container"]
        
        dkm_container = st.text_input(
            "DKM Container Name",
            value=default_container,
            help="Name for the Distributed Key Management container in Active Directory"
        )
    else:
        dkm_container = "VMM_DKM"  # Default value
    
    return smb_encryption, dkm_enabled, dkm_container

def _render_password_policy():
    """Render password policy configuration options."""
    st.header("Password Policy")
    
    with st.expander("Password Policy Configuration", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            min_length = st.number_input(
                "Minimum Password Length",
                min_value=8,
                max_value=20,
                value=12,
                help="Recommended: 12 characters minimum"
            )
        
        with col2:
            complexity = st.checkbox(
                "Require Password Complexity",
                value=True,
                help="Require uppercase, lowercase, numbers, and special characters"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            expiration_days = st.number_input(
                "Password Expiration (days)",
                min_value=0,
                max_value=365,
                value=90,
                help="0 = No expiration. Recommended: 90 days"
            )
        
        with col2:
            history = st.number_input(
                "Password History",
                min_value=0,
                max_value=24,
                value=5,
                help="Number of previous passwords remembered"
            )
        
        # Create password policy configuration
        password_policy = {
            "min_length": min_length,
            "complexity": complexity,
            "expiration_days": expiration_days,
            "history": history
        }
    
    return password_policy

def _get_default_roles(deployment_type):
    """Get default roles based on deployment type."""
    if deployment_type == "hyperv":
        return [
            {
                "name": "Administrator",
                "description": "Full control over Hyper-V environment",
                "permissions": "All permissions"
            },
            {
                "name": "Hyper-V Administrator",
                "description": "Manages virtual infrastructure",
                "permissions": "Manage VMs, virtual switches"
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
        ]
    else:
        return [
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
        ]

def _render_rbac_configuration(deployment_type):
    """Render role-based access control configuration options."""
    st.header("Role-Based Access Control")
    
    # Define standard roles based on deployment type
    default_roles = _get_default_roles(deployment_type)
    
    # Allow customization of default roles
    roles = []
    
    with st.expander("Role-Based Access Control Configuration", expanded=False):
        if deployment_type == "hyperv":
            st.write("Configure the roles for your Hyper-V environment.")
        else:
            st.write("Configure the roles for your VMM environment.")
        
        # Table of standard roles
        st.subheader("Standard Roles")
        
        standard_roles_df = pd.DataFrame([
            {
                "Name": role["name"],
                "Description": role["description"],
                "Permissions": role["permissions"]
            }
            for role in default_roles
        ])
        
        st.table(standard_roles_df)
        
        # Add all standard roles
        roles.extend(default_roles)
        
        # Allow adding custom roles
        st.subheader("Custom Roles")
        add_custom_roles = st.checkbox("Add custom roles", value=False)
        
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
                    
                    role_perms = st.text_area(
                        "Permissions",
                        value="",
                        key=f"role_perms_{i}"
                    )
                    
                    # Add to roles
                    roles.append({
                        "name": role_name,
                        "description": role_desc,
                        "permissions": role_perms,
                        "custom": True
                    })
    
    return roles

def _render_run_as_accounts():
    """Render run as accounts configuration options."""
    st.header("Run As Accounts")
    
    with st.expander("Run As Accounts Configuration", expanded=False):
        st.write("Configure Run As accounts for different operations.")
        
        # VMM service account (from software configuration)
        vmm_account = "DOMAIN\\svc_vmm"
        if "software" in st.session_state.configuration and "service_account" in st.session_state.configuration["software"]:
            vmm_account = st.session_state.configuration["software"]["service_account"]
        
        st.info(f"VMM Service Account: {vmm_account}")
        
        # Host Run As account
        host_account = st.text_input(
            "Host Management Account",
            value="DOMAIN\\svc_vmm_host",
            help="Account for managing Hyper-V hosts"
        )
        
        validate_result = validate_admin_account(host_account, "")
        if not validate_result["status"]:
            for error in validate_result["errors"]:
                st.error(error)
        for warning in validate_result["warnings"]:
            st.warning(warning)

def _validate_security_configuration(security_config):
    """Validate security configuration and display results."""
    # Validate security configuration
    validation_results = validate_security_configuration(security_config)
    
    # Display validation results
    if not validation_results["status"]:
        st.error("Security configuration has errors that must be corrected.")
        for error in validation_results["errors"]:
            st.error(error)
    
    for warning in validation_results["warnings"]:
        st.warning(warning)
    
    for recommendation in validation_results["recommendations"]:
        st.info(f"Recommendation: {recommendation}")
    
    return validation_results

def _render_security_visualization(security_config):
    """Render security visualization based on configuration."""
    st.subheader("Security Configuration Visualization")
    
    # Create security visualization
    fig = create_security_visualization(security_config)
    st.plotly_chart(fig)

def _render_security_recommendations(security_config):
    """Render security recommendations based on configuration."""
    st.header("Security Recommendations")
    
    # Generate security recommendations
    recommendations = generate_security_recommendations(security_config)
    
    # Group recommendations by category
    by_category = {}
    for rec in recommendations:
        category = rec["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(rec)
    
    # Display recommendations by category
    for category, recs in by_category.items():
        with st.expander(f"{category} Recommendations", expanded=True):
            for rec in recs:
                st.subheader(rec["title"])
                st.write(rec["description"])
                st.markdown(f"**Impact:** {rec['impact']}")
                st.markdown(f"**Implementation:** {rec['implementation']}")
                st.markdown("---")

def _render_security_best_practices():
    """Render security best practices."""
    st.header("Security Best Practices")
    
    best_practices = [
        "Use the principle of least privilege for all accounts",
        "Implement role-based access control",
        "Keep all systems updated with security patches",
        "Use encrypted communications for sensitive traffic",
        "Implement secure boot and code integrity where possible",
        "Regularly audit and review access permissions",
        "Use strong password policies",
        "Configure Distributed Key Management for encryption key security",
        "Isolate different network traffic types",
        "Regularly back up Active Directory to protect DKM keys"
    ]
    
    for practice in best_practices:
        st.markdown(f"- {practice}")

def render_security_settings():
    """Render the security settings page."""
    st.title("Security Settings")
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    
    if deployment_type == "hyperv":
        st.write("Configure security settings for your Hyper-V cluster. Proper security configuration is essential for protecting your virtualization environment.")
    else:
        st.write("Configure security settings for your Hyper-V cluster with SCVMM. Proper security configuration is essential for protecting your virtualization environment.")
    
    # Initialize security configuration in session state if not present
    _initialize_security_config()
    
    # Render security configurations
    host_hardening, code_integrity, update_policy = _render_host_security()
    network_isolation, ipsec_migration = _render_network_security()
    smb_encryption, dkm_enabled, dkm_container = _render_data_security()
    password_policy = _render_password_policy()
    roles = _render_rbac_configuration(deployment_type)
    _render_run_as_accounts()
    
    # Compile configuration for validation
    security_config = {
        "host_hardening": host_hardening,
        "network_isolation": network_isolation,
        "ipsec_migration": ipsec_migration,
        "smb_encryption": smb_encryption,
        "dkm": {
            "enabled": dkm_enabled,
            "container_name": dkm_container
        },
        "code_integrity": code_integrity,
        "update_policy": update_policy,
        "password_policy": password_policy,
        "roles": len(roles) > 0
    }
    
    # Security validation section
    st.header("Security Configuration Validation")
    validation_results = _validate_security_configuration(security_config)
    
    # Security visualization section
    _render_security_visualization(security_config)
    
    # Security recommendations section
    _render_security_recommendations(security_config)
    
    # Security best practices section
    _render_security_best_practices()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Navigate to storage configuration (index 5)
        st.button("Previous: Storage Configuration", key="prev_storage", 
                 on_click=lambda: setattr(st.session_state, "current_step", 5))
    
    with col2:
        next_button = st.button("Next: Generate Documentation", key="next_doc")
        if next_button:
            if not validation_results["status"]:
                st.error("Please correct the security configuration errors before proceeding.")
            else:
                _save_security_configuration(
                    host_hardening, network_isolation, ipsec_migration,
                    smb_encryption, dkm_enabled, code_integrity, update_policy,
                    password_policy, roles, dkm_container
                )
                # Update step counter to move to documentation (index 7)
                st.session_state.current_step = 7