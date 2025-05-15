import plotly.graph_objects as go
import pandas as pd
import re

def validate_security_configuration(config):
    """
    Validate a security configuration dictionary.
    Returns a dictionary with validation results.
    """
    results = {
        "status": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check required fields
    required_fields = [
        "host_hardening", 
        "network_isolation",
        "dkm"
    ]
    
    for field in required_fields:
        if field not in config:
            results["warnings"].append(f"Missing recommended security configuration: {field}")
    
    # Validate password policy if provided
    if "password_policy" in config:
        policy = config["password_policy"]
        
        if "min_length" in policy and policy["min_length"] < 12:
            results["warnings"].append("Password minimum length should be at least 12 characters")
        
        if "complexity" in policy and not policy["complexity"]:
            results["warnings"].append("Password complexity should be enabled")
    
    # Validate encryption settings
    if "smb_encryption" not in config or not config["smb_encryption"]:
        results["recommendations"].append("Enable SMB 3.0 encryption for data protection")
    
    if "ipsec_migration" not in config or not config["ipsec_migration"]:
        results["recommendations"].append("Enable IPsec for Live Migration traffic")
    
    # Validate Distributed Key Management (DKM)
    if "dkm" in config and isinstance(config["dkm"], dict):
        if "container_name" not in config["dkm"]:
            results["errors"].append("DKM container name must be specified")
            results["status"] = False
    else:
        results["errors"].append("Distributed Key Management (DKM) configuration is required")
        results["status"] = False
    
    # Check role-based access control
    if "roles" not in config or not config["roles"]:
        results["recommendations"].append("Configure role-based access control (RBAC) for VMM management")
    
    # Check for code integrity policies
    if "code_integrity" not in config or not config["code_integrity"]:
        results["recommendations"].append("Enable code integrity policies for enhanced security")
    
    # Add recommendations based on best practices
    if "host_hardening" not in config or not config["host_hardening"]:
        results["recommendations"].append("Implement host hardening with minimal Windows Server installation")
    
    if "update_policy" not in config or not config["update_policy"]:
        results["recommendations"].append("Establish a security update policy for all cluster components")
    
    if "network_isolation" not in config or not config["network_isolation"]:
        results["recommendations"].append("Implement network isolation for different traffic types")
    
    return results

def validate_admin_account(username, password):
    """
    Validate administrator account details.
    Returns a dictionary with validation results.
    """
    results = {
        "status": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Validate username
    if not username:
        results["errors"].append("Username cannot be empty")
        results["status"] = False
    elif len(username) < 3:
        results["warnings"].append("Username should be at least 3 characters long")
    
    # Validate password strength if provided
    if password:
        if len(password) < 12:
            results["warnings"].append("Password should be at least 12 characters long")
        
        # Check password complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        complexity_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if complexity_score < 3:
            results["warnings"].append("Password should contain at least 3 of the following: uppercase letters, lowercase letters, digits, and special characters")
        
        # Check for common patterns
        common_patterns = [
            r'123', r'abc', r'qwerty', r'admin', r'password', r'welcome'
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                results["warnings"].append(f"Password contains common pattern: {pattern}")
                break
    else:
        results["errors"].append("Password cannot be empty")
        results["status"] = False
    
    return results

def create_security_visualization(config):
    """
    Create a visual representation of the security configuration.
    Returns a Plotly figure.
    """
    # Define security categories and their statuses
    categories = [
        "Host OS Hardening",
        "Network Isolation",
        "IPsec for Migration",
        "SMB Encryption",
        "Distributed Key Management",
        "Role-Based Access",
        "Code Integrity",
        "Update Policy"
    ]
    
    # Determine status for each category
    statuses = []
    statuses.append(1 if config.get("host_hardening", False) else 0)
    statuses.append(1 if config.get("network_isolation", False) else 0)
    statuses.append(1 if config.get("ipsec_migration", False) else 0)
    statuses.append(1 if config.get("smb_encryption", False) else 0)
    statuses.append(1 if config.get("dkm", False) else 0)
    statuses.append(1 if config.get("roles", False) else 0)
    statuses.append(1 if config.get("code_integrity", False) else 0)
    statuses.append(1 if config.get("update_policy", False) else 0)
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for each category
    fig.add_trace(go.Bar(
        x=categories,
        y=statuses,
        marker_color=['green' if s else 'red' for s in statuses],
        text=['Enabled' if s else 'Disabled' for s in statuses],
        textposition='auto',
    ))
    
    # Update layout
    fig.update_layout(
        title="Security Configuration Status",
        yaxis=dict(
            title="Status",
            tickvals=[0, 1],
            ticktext=["Disabled", "Enabled"],
            range=[0, 1.2]
        ),
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def generate_security_recommendations(config):
    """
    Generate security recommendations based on configuration.
    Returns a list of recommendations.
    """
    recommendations = []
    
    # Host hardening recommendations
    if not config.get("host_hardening", False):
        recommendations.append({
            "category": "Host Security",
            "title": "Implement host hardening",
            "description": "Use minimal Windows Server installation to reduce attack surface.",
            "impact": "High",
            "implementation": "Install only required roles and features. Use security templates."
        })
    
    # Network security recommendations
    if not config.get("network_isolation", False):
        recommendations.append({
            "category": "Network Security",
            "title": "Implement network isolation",
            "description": "Separate networks for different traffic types.",
            "impact": "High",
            "implementation": "Use VLANs or physical separation for management, VM, and migration traffic."
        })
    
    if not config.get("ipsec_migration", False):
        recommendations.append({
            "category": "Network Security",
            "title": "Enable IPsec for Live Migration",
            "description": "Encrypt live migration traffic to protect VM data in transit.",
            "impact": "Medium",
            "implementation": "Configure IPsec on the live migration network interfaces."
        })
    
    # Data security recommendations
    if not config.get("smb_encryption", False):
        recommendations.append({
            "category": "Data Security",
            "title": "Enable SMB 3.0 encryption",
            "description": "Encrypt SMB traffic for end-to-end data protection.",
            "impact": "Medium",
            "implementation": "Configure SMB encryption on all file shares used by the cluster."
        })
    
    if not config.get("dkm", False):
        recommendations.append({
            "category": "Data Security",
            "title": "Configure Distributed Key Management",
            "description": "Securely store encryption keys in Active Directory.",
            "impact": "High",
            "implementation": "Set up DKM container in Active Directory and configure VMM to use it."
        })
    
    # Access control recommendations
    if not config.get("roles", False):
        recommendations.append({
            "category": "Access Control",
            "title": "Implement role-based access control",
            "description": "Restrict access based on job responsibilities.",
            "impact": "High",
            "implementation": "Define and assign appropriate VMM roles for different administrators."
        })
    
    # System integrity recommendations
    if not config.get("code_integrity", False):
        recommendations.append({
            "category": "System Integrity",
            "title": "Enable code integrity policies",
            "description": "Prevent unauthorized code execution.",
            "impact": "Medium",
            "implementation": "Configure code integrity policies on all hosts."
        })
    
    if not config.get("update_policy", False):
        recommendations.append({
            "category": "System Integrity",
            "title": "Establish update policy",
            "description": "Keep systems updated with security patches.",
            "impact": "High",
            "implementation": "Define and implement a regular patching schedule for all components."
        })
    
    return recommendations
