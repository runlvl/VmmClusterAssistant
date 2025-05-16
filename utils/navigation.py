"""
Navigation utility functions to ensure consistent navigation between pages.
"""
import streamlit as st

def create_navigation_callback(step_index):
    """
    Create a callback function for navigation buttons.
    This approach is more reliable than using lambdas.
    
    Args:
        step_index: The index of the step to navigate to
        
    Returns:
        A callback function that updates the current_step in session state
    """
    def navigate():
        st.session_state.current_step = step_index
    return navigate

def go_to_step(step_index):
    """
    Update the current step in the session state without a rerun.
    This provides a more direct way to navigate between steps.
    
    Args:
        step_index: The index of the step to navigate to
    """
    st.session_state.current_step = step_index

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