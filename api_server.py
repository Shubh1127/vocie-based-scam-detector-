from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import io
import wave
import tempfile
import base64
from complete_scam_detector import CompleteScamDetector
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize the scam detector
scam_detector = CompleteScamDetector()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Scam Detection API is running'
    })

@app.route('/api/analyze-audio', methods=['POST'])
def analyze_audio():
    """Analyze audio file for scam detection"""
    try:
        # Get audio data from request
        data = request.get_json()
        
        if 'audio' not in data:
            return jsonify({
                'success': False,
                'error': 'No audio data provided'
            }), 400
        
        # Decode base64 audio
        audio_base64 = data['audio']
        audio_bytes = base64.b64decode(audio_base64)
        
        # Save audio to temporary file (WebM format from browser)
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        # Convert WebM to WAV for Google STT (like two_person_test.py)
        wav_file_path = temp_file_path.replace('.webm', '.wav')
        try:
            from pydub import AudioSegment
            
            # Load WebM audio and convert to WAV
            audio = AudioSegment.from_file(temp_file_path, format="webm")
            
            # Convert to 16kHz mono WAV with 16-bit samples
            audio = audio.set_frame_rate(16000).set_channels(1)
            # Force 16-bit samples
            audio = audio.set_sample_width(2)  # 2 bytes = 16 bits
            audio.export(wav_file_path, format="wav")
            
            # Use the WAV file for transcription
            temp_file_path = wav_file_path
            print(f"✅ Converted WebM to WAV using pydub: {wav_file_path}")
            
        except Exception as e:
            print(f"⚠️ Pydub conversion failed: {e}")
            print("🔄 Trying direct WebM processing...")
            # Keep original WebM file if conversion fails
        
        try:
            # Transcribe with diarization
            print(f"🔄 Starting transcription for: {temp_file_path}")
            transcription_result = scam_detector.transcribe_with_diarization(temp_file_path)
            
            if not transcription_result:
                print("❌ Transcription failed - no result")
                return jsonify({
                    'success': False,
                    'error': 'Transcription failed'
                }), 500
            
            print("✅ Transcription successful, analyzing speakers...")
            # Analyze speakers
            analysis_results = scam_detector.analyze_speakers(transcription_result)
            print("✅ Speaker analysis completed")
            
            # Calculate overall risk score and level
            scam_detected = any(result['is_potential_scammer'] for result in analysis_results.values())
            overall_risk_score = max([result['risk_score'] for result in analysis_results.values()], default=0)
            
            # Determine risk level
            if overall_risk_score >= 0.7:
                risk_level = 'critical'
            elif overall_risk_score >= 0.4:
                risk_level = 'high'
            elif overall_risk_score >= 0.2:
                risk_level = 'medium'
            else:
                risk_level = 'safe'
            
            # Generate call summary
            call_summary = f"Call analyzed with {len(analysis_results)} speakers. "
            if scam_detected:
                call_summary += f"⚠️ SCAM DETECTED - Risk Level: {risk_level.upper()}"
            else:
                call_summary += f"✅ Safe conversation - Risk Level: {risk_level.upper()}"
            
            # Get Gemini AI suggestion and analysis
            print("🤖 Getting Gemini AI suggestion...")
            gemini_suggestion = scam_detector.get_gemini_suggestion(
                transcription_result['full_text'], 
                scam_detected, 
                risk_level
            )
            print("✅ Gemini AI suggestion received")
            
            # Run logic-based analysis to get more accurate scam detection
            logic_scam_detected, logic_reason = scam_detector.analyze_conversation_logic(
                transcription_result['full_text']
            )
            
            # Use Gemini's analysis to override scam detection
            final_scam_detected = logic_scam_detected or scam_detected
            if logic_scam_detected:
                print(f"🚨 Gemini logic detected scam: {logic_reason}")
                overall_risk_score = max(overall_risk_score, 0.9)
                risk_level = 'critical'
            
            # Format response
            print("🔄 Formatting response...")
            response_data = {
                'success': True,
                'data': {
                    'transcription': transcription_result,
                    'analysis': analysis_results,
                    'speakers_count': len(analysis_results),
                    'scam_detected': final_scam_detected,
                    'overall_risk_score': overall_risk_score,
                    'risk_level': risk_level,
                    'call_summary': call_summary,
                    'gemini_suggestion': gemini_suggestion,
                    'logic_scam_detected': logic_scam_detected,
                    'logic_reason': logic_reason
                }
            }
            
            print("✅ Response formatted successfully")
            return jsonify(response_data)
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if 'wav_file_path' in locals() and os.path.exists(wav_file_path):
                os.unlink(wav_file_path)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for debugging"""
    return jsonify({
        'message': 'API is working',
        'scam_keywords': scam_detector.scam_keywords[:5],  # Show first 5 keywords
        'high_risk_phrases': scam_detector.high_risk_phrases[:3]  # Show first 3 phrases
    })

if __name__ == '__main__':
    print("🚀 Starting Scam Detection API...")
    print("📡 API will be available at: http://localhost:5000")
    print("🔗 Frontend should connect to: http://localhost:5000/api/analyze-audio")
    print("⏱️  Timeout settings: 60 seconds for audio processing")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)


