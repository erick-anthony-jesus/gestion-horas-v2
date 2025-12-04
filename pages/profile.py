"""Página de perfil"""
import streamlit as st

def show_profile_page():
    st.title("👤 Mi Perfil")
    
    st.write(f"**Nombre:** {st.session_state['name']}")
    st.write(f"**Usuario:** {st.session_state['username']}")
    st.write(f"**Email:** {st.session_state['email']}")
    st.write(f"**Rol:** {st.session_state['role']}")
    
    if st.session_state['role'] == 'supervisor':
        st.write(f"**Área:** {st.session_state['area']}")
