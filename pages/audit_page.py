"""Página de auditoría"""
import streamlit as st
from database.audit import get_audit_log
from auth.roles import require_role
from datetime import date, datetime

@require_role(['admin'])
def show_audit_page():
    st.title("📋 Registro de Auditoría")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        date_from = st.date_input("Desde", value=date.today())
    with col2:
        date_to = st.date_input("Hasta", value=date.today())
    with col3:
        action = st.selectbox("Acción", ["Todas", "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT"])
    
    filters = {}
    if date_from:
        filters['date_from'] = date_from.isoformat()
    if date_to:
        filters['date_to'] = date_to.isoformat()
    if action != "Todas":
        filters['action'] = action
    
    audit_df = get_audit_log(limit=500, filters=filters)
    
    if not audit_df.empty:
        st.dataframe(audit_df, use_container_width=True)
        
        csv = audit_df.to_csv(index=False)
        st.download_button("📥 Exportar CSV", csv, f"auditoria_{datetime.now().strftime('%Y%m%d')}.csv")
    else:
        st.info("No hay registros")
