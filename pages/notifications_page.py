"""Página de notificaciones"""
import streamlit as st
from notifications.inapp import *

def show_notifications_page():
    st.title("🔔 Notificaciones")
    
    username = st.session_state['username']
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Marcar todas como leídas"):
            mark_all_read(username)
            st.rerun()
    
    notif_df = get_user_notifications(username)
    
    if not notif_df.empty:
        for _, notif in notif_df.iterrows():
            is_unread = notif['read'] == 0
            
            with st.container():
                st.markdown(f"""
                <div style='background: {"#fff3cd" if is_unread else "#f8f9fa"}; 
                            padding: 1rem; border-radius: 8px; margin-bottom: 1rem;
                            border-left: 4px solid {"#ffc107" if is_unread else "#6c757d"};'>
                    <h4>{notif['icon']} {notif['title']} {"🔴" if is_unread else ""}</h4>
                    <p>{notif['message']}</p>
                    <small>{notif['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if is_unread:
                    if st.button("Marcar leída", key=f"read_{notif['id']}"):
                        mark_notification_read(notif['id'])
                        st.rerun()
    else:
        st.info("No tienes notificaciones")
