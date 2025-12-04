"""Página de reportes"""
import streamlit as st
from auth.roles import require_role

@require_role(['admin', 'supervisor'])
def show_reports_page():
    st.title("📊 Reportes")
    st.info("Próximamente: Reportes y análisis")
