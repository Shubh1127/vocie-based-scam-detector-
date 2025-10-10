
const {
	PASSWORD_RESET_REQUEST_TEMPLATE,
	PASSWORD_RESET_SUCCESS_TEMPLATE,
	VERIFICATION_EMAIL_TEMPLATE,
	WELCOME_EMAIL,
	OTP_LOGIN_TEMPLATE,
	LOGIN_SUCCESS_TEMPLATE,
	CALL_ANALYSIS_RESULT_TEMPLATE,
	} = require("./EmailTemplate.js");
const nodemailer = require("nodemailer");

const transporter = nodemailer.createTransport({
	service: "gmail",
	port: 465,
	priority: "high",
	secure: true,
	auth: {
		user: process.env.EMAIL_USER || "shubhamsinghmor2312@gmail.com",
		pass: process.env.EMAIL_PASS ,
	},
});


const sendVerificationEmail = async (email, verificationToken) => {
	try {
		await transporter.sendMail({
			from: "shubhamsinghmor2312@gmail.com",
			to: email,
			subject: "Verify your email",
			html: VERIFICATION_EMAIL_TEMPLATE.replace("{verificationCode}", verificationToken),
		})
		console.log("Email sent successfully");
	} catch (error) {
		console.error(`Error sending verification`, error);

		throw new Error(`Error sending verification email: ${error}`);
	}
};

const sendWelcomeEmail = async (email, name) => {
	try {
		await transporter.sendMail({
			from: "shubhamsinghmor2312@gmail.com",
			to: email,
			subject: "Welcome Email",
			html: WELCOME_EMAIL.replace("{Name}", name),
		})

		console.log("Welcome email sent successfully");
	} catch (error) {
		console.error(`Error sending welcome email`, error);

		throw new Error(`Error sending welcome email: ${error}`);
	}
};

const sendPasswordResetEmail = async (email, resetURL) => {
	try {
		await transporter.sendMail({
			from: "shubhamsinghmor2312@gmail.com",
			to: email,
			subject: "Reset your password",
			html: PASSWORD_RESET_REQUEST_TEMPLATE.replace("{resetURL}", resetURL),
		})
	} catch (error) {
		console.error(`Error sending password reset email`, error);

		throw new Error(`Error sending password reset email: ${error}`);
	}
};

const sendResetSuccessEmail = async (email) => {
	try {
		await transporter.sendMail({
			from: "shubhamsinghmor2312@gmail.com",
			to: email,
			subject: "Password Reset Successful",
			html: PASSWORD_RESET_SUCCESS_TEMPLATE,
		})
		console.log("Password reset email sent successfully");
	} catch (error) {
		console.error(`Error sending password reset success email`, error);

		throw new Error(`Error sending password reset success email: ${error}`);
	}
};

const sendOtpLoginEmail = async (email, companyName, otpCode) => {
	try {
		await transporter.sendMail({
			from: "shubhamsinghmor2312@gmail.com",
			to: email,
			subject: "Kryos Login OTP - " + otpCode,
			html: OTP_LOGIN_TEMPLATE
				.replace("{companyName}", companyName)
				.replace("{otpCode}", otpCode),
		})
		console.log("OTP login email sent successfully");
	} catch (error) {
		console.error(`Error sending OTP login email`, error);
		throw new Error(`Error sending OTP login email: ${error}`);
	}
};

const sendLoginSuccessEmail = async (email, companyName, dashboardUrl = "http://localhost:3000/dashboard") => {
	try {
		const loginTime = new Date().toLocaleString();
		await transporter.sendMail({
			from: "shubhamsinghmor2312@gmail.com",
			to: email,
			subject: "Successful Login to Kryos Dashboard",
			html: LOGIN_SUCCESS_TEMPLATE
				.replace(/{companyName}/g, companyName)
				.replace("{email}", email)
				.replace("{loginTime}", loginTime)
				.replace("{dashboardUrl}", dashboardUrl),
		})
		console.log("Login success email sent successfully");
	} catch (error) {
		console.error(`Error sending login success email`, error);
		throw new Error(`Error sending login success email: ${error}`);
	}
};

const sendCallAnalysisEmail = async (email, userName, analysisData) => {
	try {
		// Determine risk level and color
		let riskLevel, riskColor;
		const riskScore = Math.round(analysisData.overall_risk_score * 100);
		
		if (analysisData.scam_detected || riskScore >= 70) {
			riskLevel = "🚨 HIGH RISK - SCAM DETECTED";
			riskColor = "#DC2626"; // Red
		} else if (riskScore >= 40) {
			riskLevel = "⚠️ MEDIUM RISK";
			riskColor = "#F59E0B"; // Orange
		} else {
			riskLevel = "✅ LOW RISK - SAFE";
			riskColor = "#10B981"; // Green
		}
		
		// Format analysis time
		const analysisTime = new Date(analysisData.timestamp).toLocaleString();
		
		// Format keywords
		const keywordsFound = analysisData.keywords_found && analysisData.keywords_found.length > 0 
			? analysisData.keywords_found.join(", ") 
			: "None detected";
		
		// Format scam detected status
		const scamDetected = analysisData.scam_detected ? "Yes" : "No";
		
		// Create transcription section if available
		let transcriptionSection = "";
		if (analysisData.transcription && analysisData.transcription.full_text) {
			const transcriptionText = analysisData.transcription.full_text.length > 200 
				? analysisData.transcription.full_text.substring(0, 200) + "..."
				: analysisData.transcription.full_text;
			
			transcriptionSection = `
			<div style="background-color: #F3F4F6; border-left: 4px solid #6B7280; padding: 15px; margin: 20px 0;">
				<h3 style="margin: 0 0 10px 0;">📝 Call Transcription</h3>
				<p style="margin: 0; font-style: italic;">"${transcriptionText}"</p>
			</div>`;
		}
		
		// Format AI recommendations
		const aiRecommendations = analysisData.call_summary || "No specific recommendations available.";
		
		// Replace template variables
		const emailContent = CALL_ANALYSIS_RESULT_TEMPLATE
			.replace(/{userName}/g, userName || "User")
			.replace(/{riskLevel}/g, riskLevel)
			.replace(/{riskColor}/g, riskColor)
			.replace(/{riskScore}/g, riskScore)
			.replace(/{caller}/g, analysisData.caller || "Unknown")
			.replace(/{analysisTime}/g, analysisTime)
			.replace(/{scamDetected}/g, scamDetected)
			.replace(/{keywordsFound}/g, keywordsFound)
			.replace(/{transcriptionSection}/g, transcriptionSection)
			.replace(/{aiRecommendations}/g, aiRecommendations)
			.replace(/{dashboardUrl}/g, process.env.DASHBOARD_URL || "http://localhost:3000/dashboard");
		
		await transporter.sendMail({
			from: "shubhamsinghmor2312@gmail.com",
			to: email,
			subject: `Call Analysis Complete - ${riskLevel}`,
			html: emailContent,
		});
		
		console.log(`Call analysis email sent successfully to ${email}`);
	} catch (error) {
		console.error(`Error sending call analysis email:`, error);
		throw new Error(`Error sending call analysis email: ${error}`);
	}
};

module.exports = {
	sendVerificationEmail,
	sendWelcomeEmail,
	sendPasswordResetEmail,
	sendResetSuccessEmail,
	sendOtpLoginEmail,
	sendLoginSuccessEmail,
	sendCallAnalysisEmail
};
