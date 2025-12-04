"""
Plantillas HTML para notificaciones por email
"""
from datetime import datetime

class EmailTemplates:
    
    @staticmethod
    def base_template(title, content, footer_text=""):
        """Plantilla base para todos los emails"""
        year = datetime.now().year
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    margin: 0;
                    padding: 0;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                }}
                .header {{ 
                    background: linear-gradient(135deg, #1190fd 0%, #2edcf7 100%); 
                    color: white; 
                    padding: 30px; 
                    text-align: center; 
                    border-radius: 10px 10px 0 0; 
                }}
                .content {{ 
                    background: #f9f9f9; 
                    padding: 30px; 
                }}
                .footer {{ 
                    background: #333; 
                    color: white; 
                    padding: 20px; 
                    text-align: center; 
                    border-radius: 0 0 10px 10px; 
                    font-size: 12px; 
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    background: white; 
                    border-radius: 8px; 
                    overflow: hidden; 
                    margin: 20px 0;
                }}
                th {{
                    background: #f0f0f0;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }}
                .total {{ 
                    background: #00adff; 
                    color: white; 
                    font-size: 18px; 
                }}
                .button {{
                    background: #3482f7;
                    color: white !important;
                    text-decoration:none;
                    list-style:none;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 20px 0;
                }}
                .alert {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .success {{
                    background: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                </div>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p>{footer_text if footer_text else 'Este es un correo automático, por favor no responder.'}</p>
                    <p>Sistema de Gestión de Horas © {year}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def horas_asignadas(trabajador_nombre, rubros_horas, total_horas, año):
        """Plantilla para notificar asignación de horas
        
        Args:
            trabajador_nombre: Nombre del trabajador
            rubros_horas: Lista de diccionarios [{'rubro': 'Desarrollo', 'horas': 8}, ...]
            total_horas: Total de horas
            año: Año
        """
        
        # Crear tabla HTML de rubros
        tabla_rubros = ""
        
        # Soportar tanto dict como lista de dicts
        if isinstance(rubros_horas, dict):
            # Formato antiguo: {'Desarrollo': 8, 'Diseño': 4}
            for rubro, horas in rubros_horas.items():
                tabla_rubros += f"""
                <tr>
                    <td>{rubro}</td>
                    <td style="text-align: right;"><strong>{horas}h</strong></td>
                </tr>
                """
        else:
            # Formato nuevo: [{'rubro': 'Desarrollo', 'horas': 8}, ...]
            for item in rubros_horas:
                tabla_rubros += f"""
                <tr>
                    <td>{item['rubro']}</td>
                    <td style="text-align: right;"><strong>{item['horas']}h</strong></td>
                </tr>
                """
        
        content = f"""
            <p>Hola <strong>{trabajador_nombre}</strong>,</p>
            <p>Se te han asignado las siguientes horas para el año {año}:</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Rubro</th>
                        <th style="text-align: right;">Horas</th>
                    </tr>
                </thead>
                <tbody>
                    {tabla_rubros}
                </tbody>
                <tfoot>
                    <tr class="total">
                        <td><strong>TOTAL</strong></td>
                        <td style="text-align: right;"><strong>{total_horas}h</strong></td>
                    </tr>
                </tfoot>
            </table>
            
            <p>Puedes ver más detalles ingresando al sistema de gestión de horas.</p>
            
            <div style="text-align: center;">
                <a href="{os.getenv('APP_URL', 'http://localhost:8501')}" class="button">
                    Ver en el Sistema
                </a>
            </div>
        """
        
        return EmailTemplates.base_template(f"🎯 Horas Asignadas {año}", content)
    
    @staticmethod
    def cambio_horas(trabajador_nombre, rubro, horas_anterior, horas_nueva, modificado_por):
        """Plantilla para notificar cambios de horas"""
        
        content = f"""
            <p>Hola <strong>{trabajador_nombre}</strong>,</p>
            <p>Se ha modificado tu asignación de horas:</p>
            
            <div class="alert">
                <p style="margin: 5px 0;"><strong>Rubro:</strong> {rubro}</p>
                <p style="margin: 5px 0;"><strong>Horas anteriores:</strong> {horas_anterior}h</p>
                <p style="margin: 5px 0;"><strong>Horas nuevas:</strong> 
                   <span style="color: #ff9800; font-size: 20px;">{horas_nueva}h</span>
                </p>
                <p style="margin: 5px 0;"><strong>Modificado por:</strong> {modificado_por}</p>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                Si tienes dudas sobre este cambio, contacta a tu supervisor.
            </p>
        """
        
        return EmailTemplates.base_template("⚠️ Modificación de Horas", content)
    
    @staticmethod
    def recordatorio_semanal(trabajador_nombre, horas_pendientes, fecha_limite):
        """Plantilla para recordatorio semanal"""
        
        content = f"""
            <p>Hola <strong>{trabajador_nombre}</strong>,</p>
            <p>Este es un recordatorio de tus horas pendientes:</p>
            
            <div class="alert">
                <h3 style="color: #2196F3; margin-top: 0;">Horas pendientes de confirmar:</h3>
                <p style="font-size: 24px; color: #ff5722; margin: 10px 0;">
                    <strong>{horas_pendientes}h</strong>
                </p>
                <p style="color: #666;">Fecha límite: {fecha_limite}</p>
            </div>
            
            <p>Por favor, ingresa al sistema para confirmar tus horas.</p>
            
            <div style="text-align: center;">
                <a href="{os.getenv('APP_URL', 'http://localhost:8501')}" class="button">
                    Ir al Sistema
                </a>
            </div>
        """
        
        return EmailTemplates.base_template("📅 Recordatorio Semanal", content)
    
    @staticmethod
    def alerta_sobrecarga(trabajador_nombre, horas_totales, limite, supervisor_nombre=""):
        """Plantilla para alerta de sobrecarga"""
        
        content = f"""
            <p>Hola <strong>{trabajador_nombre}</strong>,</p>
            <p><strong>⚠️ ALERTA:</strong> Has superado el límite de horas semanales permitido.</p>
            
            <div class="alert">
                <p style="margin: 5px 0;"><strong>Horas asignadas:</strong> 
                   <span style="font-size: 20px; color: #dc3545;">{horas_totales}h</span>
                </p>
                <p style="margin: 5px 0;"><strong>Límite permitido:</strong> {limite}h</p>
            </div>
            
            <p>Por favor coordina con tu supervisor{' ' + supervisor_nombre if supervisor_nombre else ''} 
               para redistribuir la carga de trabajo.</p>
        """
        
        return EmailTemplates.base_template("🚨 Alerta de Sobrecarga", content)
    
    @staticmethod
    def bienvenida(trabajador_nombre, username, password_temp):
        """Plantilla de bienvenida para nuevos usuarios"""
        
        content = f"""
            <p>¡Bienvenido/a al Sistema de Gestión de Horas, <strong>{trabajador_nombre}</strong>!</p>
            
            <div class="success">
                <p>Tu cuenta ha sido creada exitosamente. Aquí están tus credenciales de acceso:</p>
                <p style="margin: 10px 0;"><strong>Usuario:</strong> {username}</p>
                <p style="margin: 10px 0;"><strong>Contraseña temporal:</strong> 
                   <code style="background: #f5f5f5; padding: 5px 10px; border-radius: 3px;">{password_temp}</code>
                </p>
            </div>
            
            <p><strong>⚠️ Por seguridad, por favor cambia tu contraseña después del primer inicio de sesión.</strong></p>
            
            <div style="text-align: center;">
                <a href="{os.getenv('APP_URL', 'http://localhost:8501')}" class="button">
                    Iniciar Sesión
                </a>
            </div>
        """
        
        return EmailTemplates.base_template("🎉 Bienvenido al Sistema", content)
    
    @staticmethod
    def reporte_mensual(nombre, mes, año, resumen_datos):
        """Plantilla para reporte mensual"""
        
        # Crear tabla de resumen
        tabla_resumen = ""
        for item in resumen_datos:
            tabla_resumen += f"""
            <tr>
                <td>{item['concepto']}</td>
                <td style="text-align: right;"><strong>{item['valor']}</strong></td>
            </tr>
            """
        
        content = f"""
            <p>Hola <strong>{nombre}</strong>,</p>
            <p>Aquí está tu reporte mensual de {mes} {año}:</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Concepto</th>
                        <th style="text-align: right;">Valor</th>
                    </tr>
                </thead>
                <tbody>
                    {tabla_resumen}
                </tbody>
            </table>
            
            <p>Para más detalles, ingresa al sistema.</p>
        """
        
        return EmailTemplates.base_template(f"📊 Reporte Mensual - {mes} {año}", content)

import os
