from fastapi_mail import FastMail, MessageSchema, MessageType

from app.core.config import email_conf
from app.core.db import db
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
        return f"""
        <html>
            <body>
                <h1>Hola {user.name}</h1>
                <p>Este es tu recordatorio de <strong>{reminder.title}</strong></p>
                {f"<p>Descripción: {reminder.description}</p>" if reminder.description else ""}
                <p>Fecha de finalización: {reminder.finishDate.strftime('%d/%m/%Y %H:%M')}</p>
                <br>
                <p>Saludos, <br>El equipo de Cuentame Más</p>
            </body>
        </html>
        """
