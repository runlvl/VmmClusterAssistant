import streamlit as st
import os
from pathlib import Path

def render_installation_documentation():
    """Render the installation documentation page."""
    
    # Get deployment type from session state
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")

    st.title("Installation Guide")
    
    if deployment_type == "hyperv":
        st.markdown("""
        ## Hyper-V Cluster Implementation Tool Installation Guide
        
        This page provides information on how to install and set up the Hyper-V Cluster Implementation Tool
        in your environment.
        """)
    else:
        st.markdown("""
        ## Hyper-V Cluster with SCVMM Implementation Tool Installation Guide
        
        This page provides information on how to install and set up the Hyper-V Cluster with SCVMM Implementation Tool
        in your environment.
        """)
    
    # Check if the installation guide exists
    installation_guide_path = Path(__file__).parent.parent / "docs" / "installation_guide.md"
    
    if installation_guide_path.exists():
        with open(installation_guide_path, "r") as f:
            installation_content = f.read()
        
        # Skip the title as we already have one
        if installation_content.startswith("# "):
            installation_content = installation_content.split("\n", 1)[1]
        
        st.markdown(installation_content)
    else:
        st.warning("Installation guide not found. Please check the documentation directory.")
    
    # System requirements section
    st.header("Current System Information")
    
    import platform
    import psutil
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Operating System")
        st.info(f"{platform.system()} {platform.release()}")
        
        st.subheader("Python Version")
        st.info(f"Python {platform.python_version()}")
        
        st.subheader("Processor")
        st.info(platform.processor())
    
    with col2:
        st.subheader("Memory")
        memory = psutil.virtual_memory()
        st.info(f"Total: {memory.total / (1024**3):.2f} GB\nAvailable: {memory.available / (1024**3):.2f} GB")
        
        st.subheader("Disk Space")
        disk = psutil.disk_usage('/')
        st.info(f"Total: {disk.total / (1024**3):.2f} GB\nFree: {disk.free / (1024**3):.2f} GB")
    
    # Dependency status
    st.header("Dependency Status")
    
    from utils.dependency_checker import check_dependencies, install_all_dependencies
    
    dependency_status = check_dependencies()
    
    if dependency_status["status"]:
        st.success("✅ All required dependencies are installed")
    else:
        st.error(f"❌ Missing dependencies: {', '.join(dependency_status['missing'])}")
        
        if st.button("Install Missing Dependencies"):
            with st.spinner("Installing dependencies..."):
                install_result = install_all_dependencies()
                if install_result["status"]:
                    st.success("✅ All dependencies installed successfully")
                else:
                    st.error(f"❌ Failed to install: {', '.join(install_result['failed'])}")
                    st.info("Try installing the packages manually:\n```\npip install " + " ".join(install_result["failed"]) + "\n```")
    
    # Offline installation options
    st.header("Offline Installation")
    
    # Get deployment type to customize file name
    deployment_type = st.session_state.configuration.get("deployment_type", "hyperv")
    file_prefix = "hyperv" if deployment_type == "hyperv" else "hyperv_scvmm"
    
    if st.button("Generate Offline Installation Script"):
        from utils.dependency_checker import get_offline_installation_script
        
        script = get_offline_installation_script()
        st.code(script, language="bash")
        
        # Option to download the script
        script_path = Path(__file__).parent.parent / "offline_install.sh"
        with open(script_path, "w") as f:
            f.write(script)
        
        st.download_button(
            label="Download Installation Script",
            data=script,
            file_name=f"{file_prefix}_tool_offline_install.sh",
            mime="text/plain"
        )
        
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Navigate to introduction (index 0)
        st.button("Previous: Introduction", key="prev_intro", 
                 on_click=lambda: setattr(st.session_state, "current_step", 0))
    
    with col2:
        # Navigate to hardware requirements (index 2)
        st.button("Next: Hardware Requirements", key="next_hardware", 
                 on_click=lambda: setattr(st.session_state, "current_step", 2))