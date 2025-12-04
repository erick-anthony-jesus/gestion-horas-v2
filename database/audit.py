"""
Sistema de auditoría para registrar todas las acciones
"""
import sqlite3
import streamlit as st
from datetime import datetime
import json
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'auditoria.db'

def init_audit_db():
    """Inicializar base de datos de auditoría"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            user_role TEXT NOT NULL,
            action TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id INTEGER,
            old_value TEXT,
            new_value TEXT,
            details TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_action(action, table_name, record_id=None, old_value=None, new_value=None, details=None):
    """Registrar acción en el log de auditoría"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO audit_log 
            (timestamp, username, user_role, action, table_name, record_id, old_value, new_value, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            st.session_state.get('username', 'anonymous'),
            st.session_state.get('role', 'unknown'),
            action,
            table_name,
            record_id,
            json.dumps(old_value, ensure_ascii=False) if old_value else None,
            json.dumps(new_value, ensure_ascii=False) if new_value else None,
            details
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error registrando auditoría: {e}")
        return False

def get_audit_log(limit=100, filters=None):
    """Obtener registros de auditoría"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        
        query = "SELECT * FROM audit_log"
        params = []
        
        if filters:
            conditions = []
            if 'username' in filters and filters['username']:
                conditions.append("username = ?")
                params.append(filters['username'])
            if 'action' in filters and filters['action']:
                conditions.append("action = ?")
                params.append(filters['action'])
            if 'date_from' in filters and filters['date_from']:
                conditions.append("DATE(timestamp) >= ?")
                params.append(filters['date_from'])
            if 'date_to' in filters and filters['date_to']:
                conditions.append("DATE(timestamp) <= ?")
                params.append(filters['date_to'])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    except Exception as e:
        st.error(f"Error obteniendo logs: {e}")
        return pd.DataFrame()

def get_recent_actions(limit=10):
    """Obtener acciones recientes"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        query = """
            SELECT timestamp, username, action, table_name, details 
            FROM audit_log 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error obteniendo acciones recientes: {e}")
        return pd.DataFrame()

def get_user_stats(username=None):
    """Obtener estadísticas de usuario"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        
        if username:
            query = """
                SELECT action, COUNT(*) as count
                FROM audit_log
                WHERE username = ?
                GROUP BY action
                ORDER BY count DESC
            """
            params = [username]
        else:
            query = """
                SELECT action, COUNT(*) as count
                FROM audit_log
                GROUP BY action
                ORDER BY count DESC
            """
            params = []
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error obteniendo estadísticas: {e}")
        return pd.DataFrame()

def clear_old_logs(days=90):
    """Eliminar logs antiguos (por defecto más de 90 días)"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        c.execute("""
            DELETE FROM audit_log
            WHERE DATE(timestamp) < DATE('now', ?)
        """, (f'-{days} days',))
        
        deleted = c.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    except Exception as e:
        st.error(f"Error limpiando logs: {e}")
        return 0
