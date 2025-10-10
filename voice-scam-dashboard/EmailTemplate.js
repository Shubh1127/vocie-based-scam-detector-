const VERIFICATION_EMAIL_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify Your Email</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(to right, #4CAF50, #45a049); padding: 20px; text-align: center;">
    <h1 style="color: white; margin: 0;">Verify Your Email</h1>
  </div>
  <div style="background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <p>Hello,</p>
    <p>Thank you for signing up! Your verification code is:</p>
    <div style="text-align: center; margin: 30px 0;">
      <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #4CAF50;">{verificationCode}</span>
    </div>
    <p>Enter this code on the verification page to complete your registration.</p>
    <p>This code will expire in 15 minutes for security reasons.</p>
    <p>If you didn't create an account with us, please ignore this email.</p>
    <p>Best regards,<br>Your App Team</p>
  </div>
  <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
    <p>This is an automated message, please do not reply to this email.</p>
  </div>
</body>
</html>
`;

const WELCOME_EMAIL=`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Welcome Email</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      padding: 0;
    }

    .container {
      max-width: 600px;
      margin: 50px auto;
      background-color: #ffffff;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      overflow: hidden;
    }

    .header {
      background-color: #339933;
      padding: 20px;
      text-align: center;
    }

    .header h1 {
      color: #ffffff;
      margin: 0;
      font-size: 28px;
    }

    .content {
      padding: 30px;
      text-align: center;
      line-height: 1.6;
    }

    .content h2 {
      color: #333333;
    }

    .content p {
      color: #666666;
      margin: 20px 0;
    }

    .btn {
      display: inline-block;
      background-color: #339933;
      color: #ffffff;
      text-decoration: none;
      padding: 12px 24px;
      border-radius: 5px;
      margin-top: 20px;
    }

    .btn:hover {
      background-color: #2a7a2a;
    }

    .footer {
      background-color: #f1f1f1;
      padding: 15px;
      text-align: center;
      font-size: 12px;
      color: #888888;
    }

    @media (max-width: 600px) {
      .content {
        padding: 20px;
      }

      .header h1 {
        font-size: 24px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Welcome to Our Community!</h1>
    </div>

    <div class="content">
      <h2>Hello, {Name}! 🎉</h2>
      <p>We're excited to have you join us on this amazing journey. With your skills in Node.js, we're confident that together we will build incredible things.</p>
      <p>Whether you're working on APIs, microservices, or backend systems, we're here to support you every step of the way.</p>
      <a href="[Add_Link]" class="btn">Get Started with Node.js</a>
    </div>

    <div class="footer">
      <p>Need help? Reach out to us anytime at <a href="mailto:support@yourcompany.com">support@yourcompany.com</a></p>
      <p>&copy; 2024 [Your Company]. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
`

const PASSWORD_RESET_SUCCESS_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Password Reset Successful</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(to right, #4CAF50, #45a049); padding: 20px; text-align: center;">
    <h1 style="color: white; margin: 0;">Password Reset Successful</h1>
  </div>
  <div style="background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <p>Hello,</p>
    <p>We're writing to confirm that your password has been successfully reset.</p>
    <div style="text-align: center; margin: 30px 0;">
      <div style="background-color: #4CAF50; color: white; width: 50px; height: 50px; line-height: 50px; border-radius: 50%; display: inline-block; font-size: 30px;">
        ✓
      </div>
    </div>
    <p>If you did not initiate this password reset, please contact our support team immediately.</p>
    <p>For security reasons, we recommend that you:</p>
    <ul>
      <li>Use a strong, unique password</li>
      <li>Enable two-factor authentication if available</li>
      <li>Avoid using the same password across multiple sites</li>
    </ul>
    <p>Thank you for helping us keep your account secure.</p>
    <p>Best regards,<br>Your App Team</p>
  </div>
  <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
    <p>This is an automated message, please do not reply to this email.</p>
  </div>
</body>
</html>
`;

const OTP_LOGIN_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kryos Login OTP</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(to right, #6B46C1, #9333EA); padding: 20px; text-align: center;">
    <h1 style="color: white; margin: 0;">Kryos Login OTP</h1>
  </div>
  <div style="background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <p>Hello {companyName},</p>
    <p>You requested to sign in to your Kryos dashboard. Your login OTP is:</p>
    <div style="text-align: center; margin: 30px 0;">
      <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #6B46C1; background-color: #EDE9FE; padding: 15px 25px; border-radius: 10px; display: inline-block;">{otpCode}</span>
    </div>
    <p>Enter this code on the login page to access your dashboard.</p>
    <p><strong>This code will expire in 10 minutes</strong> for security reasons.</p>
    <p>If you didn't request this login, please ignore this email and secure your account.</p>
    <p>Best regards,<br>Kryos Team</p>
  </div>
  <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
    <p>This is an automated message, please do not reply to this email.</p>
  </div>
</body>
</html>
`;

const LOGIN_SUCCESS_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Successful Login to Kryos</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(to right, #10B981, #059669); padding: 20px; text-align: center;">
    <h1 style="color: white; margin: 0;">Welcome to Kryos!</h1>
  </div>
  <div style="background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <p>Hello {companyName},</p>
    <p>You have successfully logged in to your Kryos dashboard.</p>
    <div style="text-align: center; margin: 30px 0;">
      <div style="background-color: #10B981; color: white; width: 60px; height: 60px; line-height: 60px; border-radius: 50%; display: inline-block; font-size: 30px;">
        ✓
      </div>
    </div>
    <div style="background-color: #ECFDF5; border-left: 4px solid #10B981; padding: 15px; margin: 20px 0;">
      <p style="margin: 0; font-weight: bold;">Login Details:</p>
      <p style="margin: 5px 0;"><strong>Time:</strong> {loginTime}</p>
      <p style="margin: 5px 0;"><strong>Company:</strong> {companyName}</p>
      <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
    </div>
    <p>You can now access all your monitoring data, analytics, and manage your API keys.</p>
    <div style="text-align: center; margin: 30px 0;">
      <a href="{dashboardUrl}" style="background-color: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Go to Dashboard</a>
    </div>
    <p>If this wasn't you, please contact our support team immediately.</p>
    <p>Best regards,<br>Kryos Team</p>
  </div>
  <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
    <p>This is an automated message, please do not reply to this email.</p>
  </div>
</body>
</html>
`;

const PASSWORD_RESET_REQUEST_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Your Password</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(to right, #4CAF50, #45a049); padding: 20px; text-align: center;">
    <h1 style="color: white; margin: 0;">Password Reset</h1>
  </div>
  <div style="background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <p>Hello,</p>
    <p>We received a request to reset your password. If you didn't make this request, please ignore this email.</p>
    <p>To reset your password, click the button below:</p>
    <div style="text-align: center; margin: 30px 0;">
      <a href="{resetURL}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
    </div>
    <p>This link will expire in 1 hour for security reasons.</p>
    <p>Best regards,<br>Your App Team</p>
  </div>
  <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
    <p>This is an automated message, please do not reply to this email.</p>
  </div>
</body>
</html>
`;

const CALL_ANALYSIS_RESULT_TEMPLATE = `
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
    <p>Hello {userName},</p>
    <p>Your call analysis has been completed. Here are the results:</p>
    
    <div style="background-color: {riskColor}; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
      <h2 style="margin: 0; text-align: center;">{riskLevel}</h2>
      <p style="margin: 5px 0; text-align: center; font-size: 18px;">Risk Score: {riskScore}%</p>
    </div>
    
    <div style="background-color: #ECFDF5; border-left: 4px solid #10B981; padding: 15px; margin: 20px 0;">
      <h3 style="margin: 0 0 10px 0;">📊 Analysis Summary</h3>
      <p style="margin: 5px 0;"><strong>Caller:</strong> {caller}</p>
      <p style="margin: 5px 0;"><strong>Analysis Time:</strong> {analysisTime}</p>
      <p style="margin: 5px 0;"><strong>Scam Detected:</strong> {scamDetected}</p>
      <p style="margin: 5px 0;"><strong>Keywords Found:</strong> {keywordsFound}</p>
    </div>
    
    {transcriptionSection}
    
    <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; margin: 20px 0;">
      <h3 style="margin: 0 0 10px 0;">🤖 AI Recommendations</h3>
      <div style="white-space: pre-line;">{aiRecommendations}</div>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
      <a href="{dashboardUrl}" style="background-color: #0F172A; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Full Dashboard</a>
    </div>
    
    <p>Stay vigilant and keep your communications secure!</p>
    <p>Best regards,<br>Voice Scam Detector Team</p>
  </div>
  <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
    <p>This is an automated message, please do not reply to this email.</p>
  </div>
</body>
</html>
`;

module.exports = {
	VERIFICATION_EMAIL_TEMPLATE,
	WELCOME_EMAIL,
	PASSWORD_RESET_SUCCESS_TEMPLATE,
	OTP_LOGIN_TEMPLATE,
	LOGIN_SUCCESS_TEMPLATE,
	PASSWORD_RESET_REQUEST_TEMPLATE,
	CALL_ANALYSIS_RESULT_TEMPLATE
};