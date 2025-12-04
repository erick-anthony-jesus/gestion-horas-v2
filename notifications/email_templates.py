"""
Plantillas de Email
Templates HTML profesionales para notificaciones
"""

from datetime import datetime

class EmailTemplates:
    
    @staticmethod
    def _base_template(title, content, footer_text=None):
        """Template base para todos los emails"""
        current_year = datetime.now().year
        footer = footer_text or f"Sistema de Gestión de Horas © {current_year}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 40px 30px;
                    background: #ffffff;
                }}
                .footer {{
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .btn:hover {{
                    background: #5568d3;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                }}
                th {{
                    background: #f8f9fa;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                    border-bottom: 2px solid #dee2e6;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #dee2e6;
                }}
                .highlight {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .success-box {{
                    background: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .warning-box {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .total-row {{
                    background: #667eea;
                    color: white;
                    font-weight: 600;
                    font-size: 18px;
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
                    <p>{footer}</p>
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def horas_asignadas(trabajador_nombre, rubros_horas, total_horas, año, app_url=None):
        """Plantilla para notificar asignación de horas"""
        
        # Crear tabla HTML de rubros
        tabla_rubros = ""
        for rubro, horas in rubros_horas.items():
            tabla_rubros += f"""
            <tr>
                <td>{rubro}</td>
                <td style="text-align: right;"><strong>{horas}h</strong></td>
            </tr>
            """
        
        content = f"""
        <p>Hola <strong>{trabajador_nombre}</strong>,</p>
        <p>Se te han asignado las siguientes horas para el año <strong>{año}</strong>:</p>
        
        <table>
            <thead>
                <tr>
                    <th>Rubro</th>
                    <th style="text-align: right;">Horas Asignadas</th>
                </tr>
            </thead>
            <tbody>
                {tabla_rubros}
            </tbody>
            <tfoot>
                <tr class="total-row">
                    <td>TOTAL</td>
                    <td style="text-align: right;"><strong>{total_horas}h</strong></td>
                </tr>
            </tfoot>
        </table>
        
        <p>Puedes revisar más detalles ingresando al sistema de gestión de horas.</p>
        """
        
        if app_url:
            content += f"""
            <div style="text-align: center;">
                <a href="{app_url}" class="btn">Ver en el Sistema</a>
            </div>
            """
        
        return EmailTemplates._base_template(f"🎯 Horas Asignadas {año}", content)
    
    @staticmethod
    def cambio_horas(trabajador_nombre, rubro, horas_anterior, horas_nueva, modificado_por, motivo=None):
        """Plantilla para notificar cambios en horas"""
        
        diferencia = horas_nueva - horas_anterior
        signo = "+" if diferencia > 0 else ""
        
        content = f"""
        <p>Hola <strong>{trabajador_nombre}</strong>,</p>
        <p>Se ha realizado una modificación en tu asignación de horas:</p>
        
        <div class="warning-box">
            <p style="margin: 0;"><strong>Rubro:</strong> {rubro}</p>
            <p style="margin: 10px 0 0 0;"><strong>Cambio:</strong> 
               {horas_anterior}h → <span style="color: #ff9800; font-size: 20px;">{horas_nueva}h</span>
               ({signo}{diferencia}h)
            </p>
            <p style="margin: 10px 0 0 0;"><strong>Modificado por:</strong> {modificado_por}</p>
        """
        
        if motivo:
            content += f"""
            <p style="margin: 10px 0 0 0;"><strong>Motivo:</strong> {motivo}</p>
            """
        
        content += """
        </div>
        
        <p style="color: #666; font-size: 14px;">
            Si tienes dudas sobre este cambio, contacta a tu supervisor.
        </p>
        """
        
        return EmailTemplates._base_template("⚠️ Modificación de Horas", content)
    
    @staticmethod
    def recordatorio_semanal(trabajador_nombre, horas_pendientes, fecha_limite):
        """Recordatorio de horas pendientes"""
        
        content = f"""
        <p>Hola <strong>{trabajador_nombre}</strong>,</p>
        <p>Este es un recordatorio de tus horas pendientes de confirmar:</p>
        
        <div class="highlight">
            <h3 style="color: #2196F3; margin-top: 0;">Horas Pendientes</h3>
            <p style="font-size: 28px; color: #ff5722; margin: 10px 0;">
                <strong>{horas_pendientes}h</strong>
            </p>
            <p style="color: #666; margin-bottom: 0;">
                <strong>Fecha límite:</strong> {fecha_limite}
            </p>
        </div>
        
        <p>Por favor, ingresa al sistema para confirmar tus horas antes de la fecha límite.</p>
        """
        
        return EmailTemplates._base_template("📅 Recordatorio Semanal", content)
    
    @staticmethod
    def reporte_mensual(supervisor_nombre, area, estadisticas, mes, año):
        """Reporte mensual para supervisores"""
        
        content = f"""
        <p>Hola <strong>{supervisor_nombre}</strong>,</p>
        <p>Aquí está el reporte mensual del área de <strong>{area}</strong> para {mes} {año}:</p>
        
        <table>
            <thead>
                <tr>
                    <th>Métrica</th>
                    <th style="text-align: right;">Valor</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Total de trabajadores</td>
                    <td style="text-align: right;"><strong>{estadisticas.get('total_trabajadores', 0)}</strong></td>
                </tr>
                <tr>
                    <td>Horas asignadas</td>
                    <td style="text-align: right;"><strong>{estadisticas.get('horas_asignadas', 0)}h</strong></td>
                </tr>
                <tr>
                    <td>Horas confirmadas</td>
                    <td style="text-align: right;"><strong>{estadisticas.get('horas_confirmadas', 0)}h</strong></td>
                </tr>
                <tr>
                    <td>Tasa de confirmación</td>
                    <td style="text-align: right;"><strong>{estadisticas.get('tasa_confirmacion', 0)}%</strong></td>
                </tr>
            </tbody>
        </table>
        
        <div class="success-box">
            <p style="margin: 0;"><strong>Estado General:</strong> {estadisticas.get('estado', 'Normal')}</p>
        </div>
        """
        
        return EmailTemplates._base_template(f"📊 Reporte Mensual - {mes} {año}", content)
    
    @staticmethod
    def alerta_sobrecarga(trabajador_nombre, supervisor_nombre, horas_totales, limite):
        """Alerta de sobrecarga de horas"""
        
        exceso = horas_totales - limite
        
        content = f"""
        <p>Hola <strong>{supervisor_nombre}</strong>,</p>
        <p>Se ha detectado una posible sobrecarga de horas:</p>
        
        <div class="warning-box">
            <p style="margin: 0;"><strong>Trabajador:</strong> {trabajador_nombre}</p>
            <p style="margin: 10px 0;"><strong>Horas asignadas:</strong> 
               <span style="color: #ff5722; font-size: 24px;">{horas_totales}h</span>
            </p>
            <p style="margin: 10px 0 0 0;"><strong>Límite recomendado:</strong> {limite}h</p>
            <p style="margin: 10px 0 0 0;"><strong>Exceso:</strong> +{exceso}h</p>
        </div>
        
        <p>Por favor, revisa la asignación de horas para este trabajador.</p>
        """
        
        return EmailTemplates._base_template("🚨 Alerta de Sobrecarga", content)
    
    @staticmethod
    def bienvenida(nombre_usuario, username, password_temporal, app_url):
        """Email de bienvenida para nuevos usuarios"""
        
        content = f"""
        <p>¡Bienvenido/a <strong>{nombre_usuario}</strong>!</p>
        <p>Tu cuenta ha sido creada exitosamente en el Sistema de Gestión de Horas.</p>
        
        <div class="success-box">
            <p style="margin: 0;"><strong>Usuario:</strong> {username}</p>
            <p style="margin: 10px 0 0 0;"><strong>Contraseña temporal:</strong> {password_temporal}</p>
        </div>
        
        <p style="color: #d32f2f;"><strong>⚠️ Importante:</strong> Por seguridad, debes cambiar tu contraseña en el primer inicio de sesión.</p>
        
        <div style="text-align: center;">
            <a href="{app_url}" class="btn">Ingresar al Sistema</a>
        </div>
        """
        
        return EmailTemplates._base_template("🎉 Bienvenido al Sistema", content)
    
    @staticmethod
    def password_reset(nombre_usuario, nueva_password):
        """Email de recuperación de contraseña"""
        
        content = f"""
        <p>Hola <strong>{nombre_usuario}</strong>,</p>
        <p>Has solicitado restablecer tu contraseña.</p>
        
        <div class="highlight">
            <p style="margin: 0;"><strong>Nueva contraseña temporal:</strong></p>
            <p style="font-size: 24px; margin: 10px 0 0 0; font-family: monospace;">
                {nueva_password}
            </p>
        </div>
        
        <p style="color: #d32f2f;">
            <strong>⚠️ Importante:</strong> Por seguridad, cambia esta contraseña inmediatamente después de iniciar sesión.
        </p>
        
        <p style="color: #666; font-size: 14px;">
            Si no solicitaste este cambio, contacta al administrador de inmediato.
        </p>
        """
        
        return EmailTemplates._base_template("🔐 Recuperación de Contraseña", content)
