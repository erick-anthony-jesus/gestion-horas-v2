"""
Servicio de notificaciones por email usando Resend
"""
import os
from dotenv import load_dotenv
import base64

load_dotenv()

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    print("⚠️ Resend no instalado. Para instalar: pip install resend")

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.sender_email = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")
        self.sender_name = os.getenv("SENDER_NAME", "Sistema de Gestión de Horas")
        
        if not RESEND_AVAILABLE:
            print("⚠️ Resend no está disponible")
        elif not self.api_key:
            print("⚠️ RESEND_API_KEY no configurada en .env")
        else:
            resend.api_key = self.api_key
    
    def send_email(self, to_email, subject, body_html, attachments=None):
        """Enviar email usando Resend"""
        if not RESEND_AVAILABLE:
            print("⚠️ Resend no instalado. Ejecuta: pip install resend")
            return False
            
        if not self.api_key:
            print("⚠️ Resend no configurado. Configura RESEND_API_KEY en .env")
            return False
        
        try:
            # Preparar email
            params = {
                "from": f"{self.sender_name} <{self.sender_email}>",
                "to": [to_email],
                "subject": subject,
                "html": body_html,
            }
            
            # Agregar archivos adjuntos si existen
            if attachments:
                params["attachments"] = []
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        encoded_file = base64.b64encode(file_data).decode()
                        
                        params["attachments"].append({
                            "filename": os.path.basename(file_path),
                            "content": encoded_file,
                        })
            
            # Enviar
            email = resend.Emails.send(params)
            
            print(f"✅ Email enviado a {to_email} (ID: {email.get('id', 'N/A')})")
            return True
                
        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            return False
    
    def send_bulk_emails(self, recipients, subject, body_html):
        """Enviar email masivo"""
        results = {'success': 0, 'failed': 0}
        
        for email in recipients:
            if self.send_email(email, subject, body_html):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        return results
