"""
Servicio de notificaciones por WhatsApp usando Twilio
"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️ Twilio no instalado. Para instalar: pip install twilio")

class WhatsAppService:
    def __init__(self):
        if not TWILIO_AVAILABLE:
            self.client = None
            return
        
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("⚠️ Credenciales de Twilio no configuradas")
    
    def send_message(self, to_number, message):
        """Enviar mensaje de WhatsApp"""
        if not self.client:
            print("⚠️ Cliente de Twilio no inicializado")
            return None
        
        try:
            # Formatear número (debe incluir prefijo del país)
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            message = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=to_number
            )
            
            print(f"✅ WhatsApp enviado a {to_number}")
            return message.sid
        except Exception as e:
            print(f"❌ Error enviando WhatsApp: {e}")
            return None
    
    def send_template_message(self, to_number, template_data):
        """Enviar mensaje con plantilla"""
        message_body = self._format_template(template_data)
        return self.send_message(to_number, message_body)
    
    def _format_template(self, data):
        """Formatear plantilla de mensaje"""
        if data['type'] == 'horas_asignadas':
            # Construir tabla de rubros
            rubros_texto = ""
            if 'rubros' in data:
                for item in data['rubros']:
                    rubros_texto += f"• {item['rubro']}: {item['horas']}h\n"
            
            mensaje = f"""🎯 *Horas Asignadas {data['año']}*

Hola *{data['nombre']}*,

Se te han asignado las siguientes horas:

{rubros_texto}
━━━━━━━━━━━━━━━
📊 *Total: {data['total_horas']}h*

Ingresa al sistema para más detalles.
            """
            return mensaje.strip()
        
        elif data['type'] == 'cambio_urgente':
            return f"""
⚠️ *Cambio Importante*

{data['nombre']}, se ha modificado tu asignación:

Rubro: {data['rubro']}
Antes: {data['horas_anterior']}h
Ahora: {data['horas_nueva']}h

Modificado por: {data['modificado_por']}
            """
        
        elif data['type'] == 'alerta_sobrecarga':
            return f"""
🚨 *Alerta de Sobrecarga*

{data['nombre']}, has superado las {data['limite']}h semanales.

Horas asignadas: {data['horas_totales']}h

Por favor coordina con tu supervisor.
            """
        
        elif data['type'] == 'recordatorio':
            return f"""
📅 *Recordatorio*

Hola {data['nombre']},

Tienes {data['horas_pendientes']}h pendientes de confirmar.

Fecha límite: {data['fecha_limite']}
            """
        
        return data.get('mensaje', 'Notificación del sistema')
    
    def send_bulk_messages(self, recipients, template_data):
        """Enviar mensajes masivos"""
        if not self.client:
            return {'success': 0, 'failed': len(recipients)}
        
        results = {'success': 0, 'failed': 0}
        
        for number in recipients:
            if self.send_template_message(number, template_data):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        return results
