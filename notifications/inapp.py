"""
Sistema de notificaciones in-app
"""
import sqlite3
from datetime import datetime
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'notifications.db'

def init_notifications_db():
    """Crear tabla de notificaciones"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            read INTEGER DEFAULT 0,
            link TEXT,
            icon TEXT DEFAULT '📢'
        )
    ''')
    
    conn.commit()
    conn.close()

def add_notification(user_id, username, type, title, message, link=None, icon="📢"):
    """Agregar notificación"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO notifications 
        (user_id, username, timestamp, type, title, message, link, icon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, datetime.now().isoformat(), type, title, message, link, icon))
    
    notification_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return notification_id

def get_user_notifications(username, unread_only=False):
    """Obtener notificaciones del usuario"""
    conn = sqlite3.connect(str(DB_PATH))
    
    query = "SELECT * FROM notifications WHERE username = ?"
    params = [username]
    
    if unread_only:
        query += " AND read = 0"
    
    query += " ORDER BY timestamp DESC LIMIT 50"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def mark_notification_read(notification_id):
    """Marcar notificación como leída"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
    
    conn.commit()
    conn.close()

def mark_all_read(username):
    """Marcar todas las notificaciones como leídas"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute("UPDATE notifications SET read = 1 WHERE username = ?", (username,))
    
    conn.commit()
    conn.close()

def delete_notification(notification_id):
    """Eliminar notificación"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
    
    conn.commit()
    conn.close()

def get_unread_count(username):
    """Obtener cantidad de notificaciones sin leer"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM notifications WHERE username = ? AND read = 0", (username,))
    
    count = c.fetchone()[0]
    conn.close()
    
    return count

def delete_old_notifications(days=30):
    """Eliminar notificaciones antiguas"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute("""
        DELETE FROM notifications
        WHERE DATE(timestamp) < DATE('now', ?)
    """, (f'-{days} days',))
    
    deleted = c.rowcount
    conn.commit()
    conn.close()
    
    return deleted

# Funciones de conveniencia para crear notificaciones comunes

def notify_horas_asignadas(username, trabajador_nombre, total_horas, año):
    """Notificar asignación de horas"""
    return add_notification(
        user_id=0,  # No usado en este contexto
        username=username,
        type='horas_asignadas',
        title='🎯 Horas Asignadas',
        message=f'Se te han asignado {total_horas}h para el año {año}',
        icon='🎯'
    )

def notify_cambio_horas(username, rubro, horas_anterior, horas_nueva, modificado_por):
    """Notificar cambio de horas"""
    return add_notification(
        user_id=0,
        username=username,
        type='cambio_horas',
        title='⚠️ Cambio de Horas',
        message=f'Rubro {rubro}: {horas_anterior}h → {horas_nueva}h (por {modificado_por})',
        icon='⚠️'
    )

def notify_sobrecarga(username, horas_totales, limite):
    """Notificar sobrecarga de horas"""
    return add_notification(
        user_id=0,
        username=username,
        type='alerta',
        title='🚨 Sobrecarga Detectada',
        message=f'Has superado el límite: {horas_totales}h / {limite}h permitidas',
        icon='🚨'
    )

def notify_recordatorio(username, horas_pendientes, fecha_limite):
    """Notificar recordatorio"""
    return add_notification(
        user_id=0,
        username=username,
        type='recordatorio',
        title='📅 Recordatorio',
        message=f'Tienes {horas_pendientes}h pendientes. Límite: {fecha_limite}',
        icon='📅'
    )

def notify_welcome(username, nombre):
    """Notificar bienvenida"""
    return add_notification(
        user_id=0,
        username=username,
        type='bienvenida',
        title='🎉 Bienvenido',
        message=f'Bienvenido/a al sistema, {nombre}!',
        icon='🎉'
    )
