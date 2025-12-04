"""
Sistema de Notificaciones In-App
Gestión de notificaciones dentro de la aplicación
"""

import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
import os

DB_PATH = 'database/notifications.db'

def init_notifications_db():
    """Crear tabla de notificaciones"""
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            read INTEGER DEFAULT 0,
            link TEXT,
            icon TEXT DEFAULT '📢',
            priority TEXT DEFAULT 'normal'
        )
    ''')
    
    # Crear índices
    c.execute('CREATE INDEX IF NOT EXISTS idx_user ON notifications(username)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_read ON notifications(read)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON notifications(timestamp)')
    
    conn.commit()
    conn.close()

def add_notification(username, type, title, message, link=None, icon="📢", priority="normal"):
    """
    Agregar una notificación
    
    Args:
        username: Usuario que recibirá la notificación
        type: Tipo de notificación (info, warning, success, error)
        title: Título de la notificación
        message: Mensaje de la notificación
        link: Link opcional
        icon: Emoji del icono
        priority: Prioridad (low, normal, high)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO notifications 
            (username, timestamp, type, title, message, link, icon, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            datetime.now().isoformat(),
            type,
            title,
            message,
            link,
            icon,
            priority
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Error agregando notificación: {e}")
        return False

def add_notification_to_all(type, title, message, icon="📢", exclude_roles=None):
    """Agregar notificación a todos los usuarios"""
    from auth import load_config
    
    config = load_config()
    usernames = config['credentials']['usernames'].keys()
    
    for username in usernames:
        user_role = config['credentials']['usernames'][username]['role']
        
        # Excluir roles si se especifican
        if exclude_roles and user_role in exclude_roles:
            continue
        
        add_notification(username, type, title, message, icon=icon)

def get_user_notifications(username, unread_only=False, limit=50):
    """
    Obtener notificaciones del usuario
    
    Args:
        username: Usuario
        unread_only: Solo notificaciones no leídas
        limit: Límite de notificaciones
    
    Returns:
        DataFrame con notificaciones
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        query = "SELECT * FROM notifications WHERE username = ?"
        params = [username]
        
        if unread_only:
            query += " AND read = 0"
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
        
    except Exception as e:
        st.error(f"Error obteniendo notificaciones: {e}")
        return pd.DataFrame()

def get_unread_count(username):
    """Obtener cantidad de notificaciones no leídas"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM notifications WHERE username = ? AND read = 0", (username,))
        count = c.fetchone()[0]
        
        conn.close()
        return count
        
    except Exception as e:
        return 0

def mark_notification_read(notification_id):
    """Marcar notificación como leída"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Error marcando notificación: {e}")
        return False

def mark_all_read(username):
    """Marcar todas las notificaciones como leídas"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("UPDATE notifications SET read = 1 WHERE username = ? AND read = 0", (username,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Error marcando notificaciones: {e}")
        return False

def delete_notification(notification_id):
    """Eliminar una notificación"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Error eliminando notificación: {e}")
        return False

def delete_all_notifications(username):
    """Eliminar todas las notificaciones de un usuario"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("DELETE FROM notifications WHERE username = ?", (username,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Error eliminando notificaciones: {e}")
        return False

def show_notifications_sidebar():
    """Mostrar panel de notificaciones en el sidebar"""
    username = st.session_state.get('username')
    if not username:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔔 Notificaciones")
        
        # Obtener notificaciones
        unread_count = get_unread_count(username)
        
        if unread_count > 0:
            st.markdown(f"**{unread_count}** nuevas notificaciones")
        else:
            st.markdown("No hay notificaciones nuevas")
        
        # Botones de acción
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Marcar todas", key="mark_all", use_container_width=True):
                mark_all_read(username)
                st.rerun()
        
        with col2:
            if st.button("🗑️ Limpiar", key="clear_all", use_container_width=True):
                delete_all_notifications(username)
                st.rerun()
        
        # Mostrar últimas notificaciones
        notif_df = get_user_notifications(username, limit=5)
        
        if not notif_df.empty:
            for _, notif in notif_df.iterrows():
                # Determinar color según tipo
                if notif['type'] == 'error':
                    color = "🔴"
                elif notif['type'] == 'warning':
                    color = "🟡"
                elif notif['type'] == 'success':
                    color = "🟢"
                else:
                    color = "🔵"
                
                # Mostrar notificación
                with st.expander(
                    f"{notif['icon']} {notif['title']}" + 
                    (f" {color}" if notif['read'] == 0 else ""),
                    expanded=(notif['read'] == 0 and notif['priority'] == 'high')
                ):
                    st.markdown(notif['message'])
                    st.caption(f"📅 {notif['timestamp'][:16]}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if notif['read'] == 0:
                            if st.button("✓", key=f"read_{notif['id']}", help="Marcar leída"):
                                mark_notification_read(notif['id'])
                                st.rerun()
                    
                    with col2:
                        if st.button("🗑️", key=f"del_{notif['id']}", help="Eliminar"):
                            delete_notification(notif['id'])
                            st.rerun()

def notify_user(username, type, title, message, **kwargs):
    """Función helper para enviar notificación rápidamente"""
    return add_notification(username, type, title, message, **kwargs)

# Tipos de notificación predefinidos
class NotificationType:
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"
    REMINDER = "reminder"

# Prioridades
class Priority:
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
