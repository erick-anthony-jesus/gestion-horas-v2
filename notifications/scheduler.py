"""
Scheduler para Tareas Automáticas
Gestión de recordatorios y notificaciones programadas
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import streamlit as st

class NotificationScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = {}
    
    def start(self):
        """Iniciar scheduler"""
        if not self.scheduler.running:
            # Recordatorio semanal - Lunes a las 9:00 AM
            self.scheduler.add_job(
                self.enviar_recordatorio_semanal,
                CronTrigger(day_of_week='mon', hour=9, minute=0),
                id='recordatorio_semanal',
                name='Recordatorio Semanal'
            )
            
            # Reporte mensual - Primer día del mes a las 8:00 AM
            self.scheduler.add_job(
                self.enviar_reporte_mensual,
                CronTrigger(day=1, hour=8, minute=0),
                id='reporte_mensual',
                name='Reporte Mensual'
            )
            
            # Verificar sobrecargas - Cada 6 horas
            self.scheduler.add_job(
                self.verificar_sobrecargas,
                'interval',
                hours=6,
                id='verificar_sobrecargas',
                name='Verificación de Sobrecargas'
            )
            
            # Limpiar notificaciones antiguas - Diario a las 2:00 AM
            self.scheduler.add_job(
                self.limpiar_notificaciones_antiguas,
                CronTrigger(hour=2, minute=0),
                id='limpiar_notificaciones',
                name='Limpieza de Notificaciones'
            )
            
            self.scheduler.start()
            print("✅ Scheduler iniciado")
    
    def stop(self):
        """Detener scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("🛑 Scheduler detenido")
    
    def enviar_recordatorio_semanal(self):
        """Enviar recordatorio semanal a todos los trabajadores"""
        from database.notifications import add_notification
        from notifications.email_service import EmailService
        from notifications.email_templates import EmailTemplates
        from auth import load_config
        
        print(f"📅 [{datetime.now()}] Enviando recordatorios semanales...")
        
        config = load_config()
        email_service = EmailService()
        
        # Obtener todos los trabajadores
        trabajadores = config['credentials']['usernames']
        
        for username, user_data in trabajadores.items():
            if user_data['role'] == 'trabajador':
                # Aquí deberías calcular horas pendientes reales
                # Por ahora usamos un placeholder
                horas_pendientes = 0  # Implementar lógica real
                
                if horas_pendientes > 0:
                    # Notificación in-app
                    add_notification(
                        username,
                        'reminder',
                        '📅 Recordatorio Semanal',
                        f'Tienes {horas_pendientes}h pendientes de confirmar',
                        icon='⏰',
                        priority='normal'
                    )
                    
                    # Email
                    html = EmailTemplates.recordatorio_semanal(
                        user_data['name'],
                        horas_pendientes,
                        "31 de Diciembre"
                    )
                    
                    email_service.send_email(
                        user_data['email'],
                        "Recordatorio: Horas pendientes",
                        html
                    )
        
        print("✅ Recordatorios semanales enviados")
    
    def enviar_reporte_mensual(self):
        """Enviar reporte mensual a supervisores"""
        from database.notifications import add_notification
        from notifications.email_service import EmailService
        from notifications.email_templates import EmailTemplates
        from auth import load_config
        
        print(f"📊 [{datetime.now()}] Generando reportes mensuales...")
        
        config = load_config()
        email_service = EmailService()
        
        mes = datetime.now().strftime("%B")
        año = datetime.now().year
        
        # Obtener supervisores
        supervisores = {u: d for u, d in config['credentials']['usernames'].items() 
                       if d['role'] == 'supervisor'}
        
        for username, user_data in supervisores.items():
            area = user_data.get('area')
            
            # Aquí deberías calcular estadísticas reales
            estadisticas = {
                'total_trabajadores': 0,  # Implementar lógica real
                'horas_asignadas': 0,
                'horas_confirmadas': 0,
                'tasa_confirmacion': 0,
                'estado': 'Normal'
            }
            
            # Notificación in-app
            add_notification(
                username,
                'info',
                f'📊 Reporte Mensual - {mes}',
                f'Reporte mensual del área de {area} disponible',
                icon='📈',
                priority='normal'
            )
            
            # Email
            html = EmailTemplates.reporte_mensual(
                user_data['name'],
                area,
                estadisticas,
                mes,
                año
            )
            
            email_service.send_email(
                user_data['email'],
                f"Reporte Mensual - {mes} {año}",
                html
            )
        
        print("✅ Reportes mensuales enviados")
    
    def verificar_sobrecargas(self):
        """Verificar trabajadores con sobrecarga de horas"""
        from database.notifications import add_notification
        from notifications.whatsapp_service import WhatsAppService, WhatsAppTemplates
        from auth import load_config
        
        print(f"🚨 [{datetime.now()}] Verificando sobrecargas...")
        
        config = load_config()
        whatsapp = WhatsAppService()
        
        LIMITE_HORAS = 40  # Límite semanal
        
        # Aquí deberías obtener trabajadores y sus horas reales
        # Por ahora es un placeholder
        
        trabajadores_sobrecargados = []  # Implementar lógica real
        
        for trabajador in trabajadores_sobrecargados:
            username = trabajador['username']
            horas_totales = trabajador['horas_totales']
            
            # Notificación al trabajador
            add_notification(
                username,
                'warning',
                '🚨 Alerta de Sobrecarga',
                f'Tienes {horas_totales}h asignadas (límite: {LIMITE_HORAS}h)',
                icon='⚠️',
                priority='high'
            )
            
            # WhatsApp si está habilitado
            if trabajador.get('whatsapp_habilitado') and trabajador.get('telefono'):
                template = WhatsAppTemplates.alerta_sobrecarga(
                    trabajador['nombre'],
                    horas_totales,
                    LIMITE_HORAS
                )
                whatsapp.send_template_message(trabajador['telefono'], template)
            
            # Notificar al supervisor
            supervisor_username = trabajador.get('supervisor_username')
            if supervisor_username:
                add_notification(
                    supervisor_username,
                    'warning',
                    '⚠️ Trabajador Sobrecargado',
                    f"{trabajador['nombre']} tiene {horas_totales}h asignadas",
                    icon='🚨',
                    priority='high'
                )
        
        print(f"✅ Verificación completada. {len(trabajadores_sobrecargados)} sobrecargas detectadas")
    
    def limpiar_notificaciones_antiguas(self):
        """Limpiar notificaciones leídas antiguas"""
        import sqlite3
        
        print(f"🧹 [{datetime.now()}] Limpiando notificaciones antiguas...")
        
        try:
            # Eliminar notificaciones leídas de más de 30 días
            fecha_limite = (datetime.now() - timedelta(days=30)).isoformat()
            
            conn = sqlite3.connect('database/notifications.db')
            c = conn.cursor()
            
            c.execute("""
                DELETE FROM notifications 
                WHERE read = 1 AND timestamp < ?
            """, (fecha_limite,))
            
            eliminadas = c.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✅ {eliminadas} notificaciones antiguas eliminadas")
            
        except Exception as e:
            print(f"❌ Error limpiando notificaciones: {e}")
    
    def get_jobs_status(self):
        """Obtener estado de los jobs programados"""
        jobs_info = []
        
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'N/A'
            
            jobs_info.append({
                'id': job.id,
                'nombre': job.name,
                'próxima_ejecución': next_run,
                'trigger': str(job.trigger)
            })
        
        return jobs_info
    
    def pause_job(self, job_id):
        """Pausar un job específico"""
        try:
            self.scheduler.pause_job(job_id)
            return True
        except Exception as e:
            print(f"Error pausando job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id):
        """Reanudar un job pausado"""
        try:
            self.scheduler.resume_job(job_id)
            return True
        except Exception as e:
            print(f"Error reanudando job {job_id}: {e}")
            return False


# Singleton global
_scheduler_instance = None

def get_scheduler():
    """Obtener instancia del scheduler (singleton)"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = NotificationScheduler()
    return _scheduler_instance

def start_scheduler():
    """Iniciar el scheduler global"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler
