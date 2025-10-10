#!/usr/bin/env python3
"""
Test script for email functionality
"""

import os
from email_service import send_call_analysis_notification

def test_email_service():
    """Test the email service with sample data"""
    print("🧪 TESTING EMAIL SERVICE")
    print("=" * 40)
    
    # Check environment variables
    email_user = os.getenv('EMAIL_USER', 'shubhamsinghmor2312@gmail.com')
    email_pass = os.getenv('EMAIL_PASS')
    
    print(f"📧 Email User: {email_user}")
    print(f"🔑 Email Pass: {'✅ Set' if email_pass else '❌ Not set'}")
    
    if not email_pass:
        print("❌ EMAIL_PASS environment variable not set!")
        print("Please set EMAIL_PASS in your .env file")
        return
    
    # Sample analysis data
    sample_analysis = {
        'timestamp': '2025-01-09T15:30:00.000Z',
        'caller': 'Unknown',
        'overall_risk_score': 0.7,  # 70% risk
        'scam_detected': True,
        'keywords_found': ['urgent', 'payment', 'verify'],
        'transcription': {
            'full_text': 'Hello, this is an urgent call about your account. Please verify your payment information immediately.'
        },
        'call_summary': 'High-risk call detected with urgent payment verification request. This appears to be a scam attempt.'
    }
    
    # Test email
    test_email = "shubhamsinghmor2312@gmail.com"  # Replace with your test email
    test_name = "Test User"
    
    print(f"\n📤 Sending test email to: {test_email}")
    print(f"📊 Sample data: {sample_analysis['overall_risk_score']*100}% risk, scam detected: {sample_analysis['scam_detected']}")
    
    try:
        result = send_call_analysis_notification(test_email, test_name, sample_analysis)
        if result:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Test email failed to send")
    except Exception as e:
        print(f"❌ Error sending test email: {e}")

if __name__ == "__main__":
    test_email_service()
