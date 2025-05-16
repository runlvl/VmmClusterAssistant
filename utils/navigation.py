"""
Navigation utility functions to ensure consistent navigation between pages.
"""
import streamlit as st

def go_to_step(step_index):
    """
    Update the current step in the session state and trigger a rerun.
    This provides a consistent way to navigate between steps.
    
    Args:
        step_index: The index of the step to navigate to
    """
    # Make sure we're not trying to navigate to the same page
    if st.session_state.current_step != step_index:
        # Update session state
        st.session_state.current_step = step_index
        # Force streamlit to rerun the app
        st.rerun()

def go_to_introduction():
    """Navigate to the Introduction page"""
    go_to_step(0)
    
def go_to_installation():
    """Navigate to the Installation page"""
    go_to_step(1)
    
def go_to_hardware():
    """Navigate to the Hardware Requirements page"""
    go_to_step(2)
    
def go_to_software():
    """Navigate to the Software Requirements page"""
    go_to_step(3)
    
def go_to_network():
    """Navigate to the Network Configuration page"""
    go_to_step(4)
    
def go_to_storage():
    """Navigate to the Storage Configuration page"""
    go_to_step(5)
    
def go_to_documentation():
    """Navigate to the Documentation page"""
    go_to_step(6)