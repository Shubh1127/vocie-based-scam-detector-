#!/usr/bin/env python3
"""
Email service for sending call analysis notifications
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USER', 'shubhamsinghmor2312@gmail.com')
        self.email_pass = os.getenv('EMAIL_PASS')
        self.dashboard_url = os.getenv('DASHBOARD_URL', 'http://localhost:3000/dashboard')
    
    def create_call_analysis_template(self, user_name, analysis_data):
        """Create HTML email template for call analysis results"""
        
        # Determine risk level and color
        risk_score = round(analysis_data.get('overall_risk_score', 0) * 100)
        
        if analysis_data.get('scam_detected') or risk_score >= 70:
            risk_level = "🚨 HIGH RISK - SCAM DETECTED"
            risk_color = "#DC2626"  # Red
        elif risk_score >= 40:
            risk_level = "⚠️ MEDIUM RISK"
            risk_color = "#F59E0B"  # Orange
        else:
            risk_level = "✅ LOW RISK - SAFE"
            risk_color = "#10B981"  # Green
        
        # Format analysis time
        timestamp = analysis_data.get('timestamp', datetime.now().isoformat())
        try:
            analysis_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
        except:
            analysis_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format keywords
        keywords_found = analysis_data.get('keywords_found', [])
        keywords_text = ", ".join(keywords_found) if keywords_found else "None detected"
        
        # Format scam detected status
        scam_detected = "Yes" if analysis_data.get('scam_detected') else "No"
        
        # Create transcription section if available
        transcription_section = ""
        transcription = analysis_data.get('transcription', {})
        if transcription and transcription.get('full_text'):
            transcription_text = transcription['full_text']
            if len(transcription_text) > 200:
                transcription_text = transcription_text[:200] + "..."
            
            transcription_section = f"""
            <div style="background-color: #F3F4F6; border-left: 4px solid #6B7280; padding: 15px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0;">📝 Call Transcription</h3>
                <p style="margin: 0; font-style: italic;">"{transcription_text}"</p>
            </div>"""
        
        # Format AI recommendations
        ai_recommendations = analysis_data.get('call_summary', 'No specific recommendations available.')
        
        # Create HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Call Analysis Complete - Voice Scam Detector</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(to right, #0F172A, #1E293B); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">🔍 Call Analysis Complete</h1>
            </div>
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <p>Hello {user_name or 'User'},</p>
                <p>Your call analysis has been completed. Here are the results:</p>
                
                <div style="background-color: {risk_color}; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="margin: 0; text-align: center;">{risk_level}</h2>
                    <p style="margin: 5px 0; text-align: center; font-size: 18px;">Risk Score: {risk_score}%</p>
                </div>
                
                <div style="background-color: #ECFDF5; border-left: 4px solid #10B981; padding: 15px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0;">📊 Analysis Summary</h3>
                    <p style="margin: 5px 0;"><strong>Caller:</strong> {analysis_data.get('caller', 'Unknown')}</p>
                    <p style="margin: 5px 0;"><strong>Analysis Time:</strong> {analysis_time}</p>
                    <p style="margin: 5px 0;"><strong>Scam Detected:</strong> {scam_detected}</p>
                    <p style="margin: 5px 0;"><strong>Keywords Found:</strong> {keywords_text}</p>
                </div>
                
                {transcription_section}
                
                <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0;">🤖 AI Recommendations</h3>
                    <div style="white-space: pre-line;">{ai_recommendations}</div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{self.dashboard_url}" style="background-color: #0F172A; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Full Dashboard</a>
                </div>
                
                <p>Stay vigilant and keep your communications secure!</p>
                <p>Best regards,<br>Voice Scam Detector Team</p>
            </div>
            <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def send_call_analysis_email(self, email, user_name, analysis_data):
        """Send call analysis results email"""
        try:
            if not self.email_pass:
                print("❌ EMAIL_PASS not configured, skipping email")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = email
            
            # Determine subject based on risk level
            risk_score = round(analysis_data.get('overall_risk_score', 0) * 100)
            if analysis_data.get('scam_detected') or risk_score >= 70:
                subject = "🚨 HIGH RISK - Call Analysis Complete"
            elif risk_score >= 40:
                subject = "⚠️ MEDIUM RISK - Call Analysis Complete"
            else:
                subject = "✅ Call Analysis Complete - Safe"
            
            msg['Subject'] = subject
            
            # Create HTML content
            html_content = self.create_call_analysis_template(user_name, analysis_data)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            print(f"✅ Call analysis email sent successfully to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending call analysis email to {email}: {e}")
            return False

# Global email service instance
email_service = EmailService()

def send_call_analysis_notification(email, user_name, analysis_data):
    """Convenience function to send call analysis email"""
    return email_service.send_call_analysis_email(email, user_name, analysis_data)
