import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
import string

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "energyforecastingai@gmail.com"
EMAIL_PASSWORD = "msmr nvle vlfv znjt"  # App password

def generate_reset_code() -> str:
    """Generate a 6-digit reset code"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def generate_otp() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def send_signup_otp_email(to_email: str, otp_code: str) -> bool:
    """Send signup OTP code via email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = "Email Verification Code - Energy Forecasting"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0284c7;">Welcome to Energy Forecasting!</h2>
                <p>Hello,</p>
                <p>Thank you for signing up for Energy Forecasting. To complete your registration, please verify your email address.</p>
                <p>Your verification code is:</p>
                <div style="background-color: #f0f9ff; border: 2px solid #0284c7; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                    <h1 style="color: #0284c7; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp_code}</h1>
                </div>
                <p>This code will expire in 10 minutes.</p>
                <p>If you did not create an account, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        return False

def send_reset_email(to_email: str, reset_code: str) -> bool:
    """Send password reset code via email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = "Password Reset Code - Energy Forecasting"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0284c7;">Password Reset Request</h2>
                <p>Hello,</p>
                <p>You have requested to reset your password for your Energy Forecasting account.</p>
                <p>Your password reset code is:</p>
                <div style="background-color: #f0f9ff; border: 2px solid #0284c7; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                    <h1 style="color: #0284c7; font-size: 32px; margin: 0; letter-spacing: 5px;">{reset_code}</h1>
                </div>
                <p>This code will expire in 15 minutes.</p>
                <p>If you did not request this password reset, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

