from email.message import EmailMessage
import smtplib
from config import Config


def smtp_is_configured() -> bool:
    return all([
        Config.SMTP_HOST,
        Config.SMTP_PORT,
        Config.SMTP_USERNAME,
        Config.SMTP_PASSWORD,
        Config.SMTP_FROM_EMAIL,
    ])


def send_welcome_email(user) -> bool:
    if not smtp_is_configured():
        return False

    message = EmailMessage()
    message["Subject"] = "Welcome to SkillRank"
    message["From"] = Config.SMTP_FROM_EMAIL
    message["To"] = user["email"]
    # Plain text version
    text_content = (
        f"Hi {user.get('name', 'there')},\n\n"
        "Welcome to SkillRank! Your account has been created successfully.\n"
        "You can now manage your profile and view the dashboard.\n\n"
        "Thanks,\nThe SkillRank Team"
    )
    message.set_content(text_content)

    # HTML version
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .email-card {{
                font-family: 'Inter', sans-serif;
                max-width: 600px;
                margin: 20px auto;
                background: #0b1120;
                color: #f1f5f9 !important;
                border-radius: 20px;
                overflow: hidden;
                border: 1px solid rgba(148,163,184,0.12);
            }}
            .header {{
                background: linear-gradient(135deg, #6366f1, #4f46e5);
                padding: 40px 20px;
                text-align: center;
            }}
            .body {{
                padding: 40px 30px;
                line-height: 1.6;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                background: #6366f1;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 600;
                margin-top: 20px;
            }}
            .footer {{
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #94a3b8;
                border-top: 1px solid rgba(148,163,184,0.12);
            }}
        </style>
    </head>
    <body style="background-color: #020617; padding: 20px;">
        <div class="email-card">
            <div class="header">
                <h1 style="margin: 0; font-size: 28px; color: white;">SkillRank</h1>
            </div>
            <div class="body">
                <h2 style="color: #6366f1;">Welcome, {user.get('name', 'User')}!</h2>
                <p style="color: #f1f5f9;">Your account has been successfully created. We're excited to have you on board!</p>
                <p style="color: #f1f5f9;">You can now log in to your dashboard to manage your skills and profile.</p>
                <a href="http://127.0.0.1:5000/login" class="btn">Go to Dashboard</a>
            </div>
            <div class="footer">
                &copy; 2026 SkillRank Team. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    message.add_alternative(html_content, subtype="html")

    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=15) as smtp:
        if Config.SMTP_USE_TLS:
            smtp.starttls()
        smtp.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        smtp.send_message(message)

    return True
