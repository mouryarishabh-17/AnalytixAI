"""
Email Service for AnalytixAI
Handles sending verification emails, password reset emails, and other notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
FROM_NAME = os.getenv("FROM_NAME", "AnalytixAI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500")


def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
    """
    Send an email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML body content
        text_content: Plain text body content (optional, falls back to HTML)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email
        
        # Add plain text version
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)
        
        # Add HTML version
        part2 = MIMEText(html_content, "html")
        message.attach(part2)
        
        # Connect to SMTP server and send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False


def send_verification_email(to_email: str, username: str, verification_token: str):
    """
    Send email verification link to user
    
    Args:
        to_email: User's email address
        username: User's name
        verification_token: Unique verification token
    
    Returns:
        bool: True if email sent successfully
    """
    verification_link = f"{FRONTEND_URL}/verify-email.html?token={verification_token}"
    
    subject = "Verify Your Email - AnalytixAI"
    
    # HTML email template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                padding: 30px;
                color: white;
            }}
            .content {{
                background: white;
                border-radius: 8px;
                padding: 30px;
                margin-top: 20px;
                color: #333;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: rgba(255,255,255,0.8);
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 10px;
                margin: 20px 0;
                color: #856404;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 AnalytixAI</h1>
            <p>Welcome to the future of data analytics!</p>
            
            <div class="content">
                <h2>Hi {username}! 👋</h2>
                <p>Thank you for registering with AnalytixAI. We're excited to have you on board!</p>
                
                <p>To complete your registration and start analyzing your data, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center;">
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </div>
                
                <div class="warning">
                    <strong>⏰ This link will expire in 24 hours.</strong><br>
                    If you didn't create an account with AnalytixAI, please ignore this email.
                </div>
                
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_link}</p>
                
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                
                <p style="font-size: 14px; color: #666;">
                    Need help? Contact us at support@analytixai.com
                </p>
            </div>
            
            <div class="footer">
                <p>© 2024 AnalytixAI - Automated Data Analytics Platform</p>
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Hi {username}!
    
    Thank you for registering with AnalytixAI.
    
    Please verify your email address by clicking this link:
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account with AnalytixAI, please ignore this email.
    
    ---
    AnalytixAI - Automated Data Analytics Platform
    """
    
    return send_email(to_email, subject, html_content, text_content)


def send_password_reset_email(to_email: str, username: str, reset_token: str):
    """
    Send password reset link to user
    
    Args:
        to_email: User's email address
        username: User's name
        reset_token: Unique reset token
    
    Returns:
        bool: True if email sent successfully
    """
    reset_link = f"{FRONTEND_URL}/reset-password.html?token={reset_token}"
    
    subject = "Reset Your Password - AnalytixAI"
    
    # HTML email template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                padding: 30px;
                color: white;
            }}
            .content {{
                background: white;
                border-radius: 8px;
                padding: 30px;
                margin-top: 20px;
                color: #333;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: rgba(255,255,255,0.8);
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 10px;
                margin: 20px 0;
                color: #856404;
            }}
            .danger {{
                background: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 10px;
                margin: 20px 0;
                color: #721c24;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 AnalytixAI</h1>
            <p>Password Reset Request</p>
            
            <div class="content">
                <h2>Hi {username}! 👋</h2>
                <p>We received a request to reset your password for your AnalytixAI account.</p>
                
                <p>Click the button below to reset your password:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </div>
                
                <div class="warning">
                    <strong>⏰ This link will expire in 1 hour.</strong>
                </div>
                
                <div class="danger">
                    <strong>⚠️ Security Notice:</strong><br>
                    If you didn't request a password reset, please ignore this email or contact support if you're concerned about your account security.
                </div>
                
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                
                <p style="font-size: 14px; color: #666;">
                    Need help? Contact us at support@analytixai.com
                </p>
            </div>
            
            <div class="footer">
                <p>© 2024 AnalytixAI - Automated Data Analytics Platform</p>
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Hi {username}!
    
    We received a request to reset your password for your AnalytixAI account.
    
    Click this link to reset your password:
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you didn't request a password reset, please ignore this email.
    
    ---
    AnalytixAI - Automated Data Analytics Platform
    """
    
    return send_email(to_email, subject, html_content, text_content)


def send_welcome_email(to_email: str, username: str):
    """
    Send welcome email after successful email verification
    
    Args:
        to_email: User's email address
        username: User's name
    
    Returns:
        bool: True if email sent successfully
    """
    subject = "Welcome to AnalytixAI! 🎉"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                padding: 30px;
                color: white;
            }}
            .content {{
                background: white;
                border-radius: 8px;
                padding: 30px;
                margin-top: 20px;
                color: #333;
            }}
            .feature {{
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: rgba(255,255,255,0.8);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Welcome to AnalytixAI!</h1>
            
            <div class="content">
                <h2>Hi {username}! 👋</h2>
                <p>Your email has been verified successfully! You're all set to start analyzing your data.</p>
                
                <h3>🚀 What you can do with AnalytixAI:</h3>
                
                <div class="feature">
                    <strong>📊 Multi-Domain Analytics</strong><br>
                    Analyze Sales, Finance, Student, and Employee data with just a few clicks.
                </div>
                
                <div class="feature">
                    <strong>🤖 AI-Powered Insights</strong><br>
                    Get intelligent insights and chat with your data using our AI assistant.
                </div>
                
                <div class="feature">
                    <strong>📈 Beautiful Visualizations</strong><br>
                    Generate stunning charts and visualizations automatically.
                </div>
                
                <div class="feature">
                    <strong>📄 PDF Reports</strong><br>
                    Download comprehensive PDF reports of your analysis.
                </div>
                
                <p style="margin-top: 30px;">Ready to get started? Log in and upload your first dataset!</p>
                
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                
                <p style="font-size: 14px; color: #666;">
                    Questions? Check out our documentation or contact support@analytixai.com
                </p>
            </div>
            
            <div class="footer">
                <p>© 2024 AnalytixAI - Automated Data Analytics Platform</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)
