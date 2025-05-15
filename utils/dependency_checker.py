import importlib
import subprocess
import sys
import os
import pkg_resources

def check_dependencies():
    """
    Check if all required dependencies are installed.
    Returns a dictionary with status and list of missing dependencies.
    """
    required_packages = [
        'streamlit',
        'pandas',
        'plotly',
        'networkx',
        'jinja2',
        'pyyaml',
        'psutil',
        'requests',
        'streamlit_option_menu'
    ]
    
    # Try to check for Windows-specific dependencies if on Windows
    if os.name == 'nt':
        required_packages.append('wmi')
    
    # Check installed packages
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = [pkg for pkg in required_packages if pkg.lower() not in installed_packages]
    
    # If on Windows, check for WMI specifically
    if os.name == 'nt' and 'wmi' not in installed_packages:
        try:
            importlib.import_module('wmi')
            # If we get here, WMI is installed but not listed in pip packages
            if 'wmi' in missing_packages:
                missing_packages.remove('wmi')
        except ImportError:
            if 'wmi' not in missing_packages:
                missing_packages.append('wmi')
    
    return {
        "status": len(missing_packages) == 0,
        "missing": missing_packages,
        "installed": list(installed_packages)
    }

def install_dependency(package_name):
    """
    Install a missing dependency using pip.
    Returns True if successful, False otherwise.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def install_all_dependencies():
    """
    Install all missing dependencies.
    Returns a dictionary with status and list of failed installations.
    """
    dependency_check = check_dependencies()
    if dependency_check["status"]:
        return {"status": True, "message": "All dependencies already installed"}
    
    failed_installations = []
    for package in dependency_check["missing"]:
        if not install_dependency(package):
            failed_installations.append(package)
    
    return {
        "status": len(failed_installations) == 0,
        "failed": failed_installations,
        "installed": [pkg for pkg in dependency_check["missing"] if pkg not in failed_installations]
    }

def get_offline_installation_script():
    """
    Generates a script that can be used to install dependencies offline.
    """
    dependencies = check_dependencies()
    if dependencies["status"]:
        return "# All dependencies are already installed"
    
    script_lines = ["# Offline dependency installation script", ""]
    
    if os.name == 'nt':  # Windows
        script_lines.append("@echo off")
        script_lines.append("echo Installing dependencies...")
        for pkg in dependencies["missing"]:
            script_lines.append(f"pip install {pkg}")
        script_lines.append("echo Installation complete!")
    else:  # Linux/macOS
        script_lines.append("#!/bin/bash")
        script_lines.append("echo 'Installing dependencies...'")
        for pkg in dependencies["missing"]:
            script_lines.append(f"pip install {pkg}")
        script_lines.append("echo 'Installation complete!'")
    
    return "\n".join(script_lines)

def download_offline_packages():
    """
    Downloads packages for offline installation.
    Returns the path to the downloaded packages.
    """
    dependencies = check_dependencies()
    if dependencies["status"]:
        return {"status": True, "message": "All dependencies already installed"}
    
    download_dir = os.path.join(os.getcwd(), "offline_packages")
    os.makedirs(download_dir, exist_ok=True)
    
    failed_downloads = []
    for package in dependencies["missing"]:
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "download", 
                "--dest", download_dir, package
            ])
        except subprocess.CalledProcessError:
            failed_downloads.append(package)
    
    return {
        "status": len(failed_downloads) == 0,
        "download_path": download_dir,
        "failed": failed_downloads,
        "downloaded": [pkg for pkg in dependencies["missing"] if pkg not in failed_downloads]
    }

if __name__ == "__main__":
    # This allows running this module directly for testing
    print("Checking dependencies...")
    result = check_dependencies()
    print(f"Status: {'All dependencies installed' if result['status'] else 'Missing dependencies'}")
    if not result["status"]:
        print(f"Missing: {', '.join(result['missing'])}")
        
        # Ask if we should install missing dependencies
        if input("Install missing dependencies? (y/n): ").lower() == 'y':
            install_result = install_all_dependencies()
            if install_result["status"]:
                print("All dependencies were successfully installed.")
            else:
                print(f"Failed to install: {', '.join(install_result['failed'])}")
