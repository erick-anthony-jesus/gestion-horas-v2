"""Página de configuración"""
import streamlit as st
from auth.roles import require_role

@require_role(['admin'])
def show_settings_page():
    st.title("⚙️ Configuración")
    st.info("Próximamente: Configuración de sistema")
