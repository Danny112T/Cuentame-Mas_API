from fastapi_mail import FastMail, MessageSchema, MessageType

from app.core.config import email_conf
from app.models.reminder import Reminder
from app.models.user import User


class EmailService:
    def __init__(self) -> None:
        self.mail = FastMail(email_conf)

    async def send_reminder_email(self,user: User, reminder: Reminder) -> None:
        message = MessageSchema(
            subject=f"Tu recordatorio de {reminder.title}",
            recipients=[user.email],
            body= self._create_reminder_email_body(user, reminder),
            subtype=MessageType.html,
        )
        await self.mail.send_message(message)

    def _create_reminder_email_body(self, user: User, reminder: Reminder) -> str:
        description_html = f"<p>Descripción: {reminder.description}</p>" if reminder.description else ""
        return f"""
        <!DOCTYPE html>
                <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Recordatorio - Cuentame Más</title>
                        <style>
                            .container {{
                                background-color: #FFFFFF;
                                margin: 0 auto;
                                padding: 20px;
                                max-width: 600px;
                                border-radius: 10px;
                                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                                text-align: center;
                                font-family: Arial, sans-serif;
                            }}
                            .header {{
                                background-color: #F7D8D8;
                                border-top-left-radius: 10px;
                                border-top-right-radius: 10px;
                                padding: 20px 10px;
                            }}
                            .header img {{
                                width: 80px;
                                height: auto;
                            }}
                            .header h1 {{
                                color: #FF6961;
                                font-size: 24px;
                                margin: 10px 0;
                            }}
                            .content {{
                                padding: 20px;
                                text-align: left;
                                color: #333333;
                            }}
                            .content h1 {{
                                font-size: 20px;
                                color: #FF6961;
                            }}
                            .content p {{
                                font-size: 16px;
                                margin: 10px 0;
                            }}
                            .footer {{
                                margin-top: 20px;
                                font-size: 12px;
                                color: #888888;
                            }}
                        </style>
                    </head>
                    <body style="margin: 0; padding: 20px; background-color: #F5F5F5;">
                        <div class="container">
                            <div class="header">
                                <img src="https://cuentame-mas.vercel.app/assets/assets/images/logo.8d0effbd4cea9808a43cf0d5edb42fca.png" alt="Logo">
                                <h1>¡Hola {user.name}!</h1>
                            </div>
                            <div class="content">
                                <h1>Recordatorio:</h1>
                                <p>Este es tu recordatorio de <strong>{reminder.title}</strong>.</p>
                                {description_html}
                                <p>Fecha de finalización: {reminder.finishDate.strftime('%d/%m/%Y %H:%M')}</p>
                                <br>
                                <p>Saludos,<br>El equipo de Cuentame Más</p>
                            </div>
                            <div class="footer">
                                © 2025 Cuentame Más. Todos los derechos reservados.
                            </div>
                        </div>
                    </body>
                </html>
        """
