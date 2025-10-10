from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import io
import wave
import tempfile
import base64
from complete_scam_detector import CompleteScamDetector
from user_model import user_model
from analyzed_call_model import analyzed_call_model
# Pinata IPFS integration
try:
    from pinata_service import get_pinata_service
    PINATA_AVAILABLE = True
except ImportError:
    PINATA_AVAILABLE = False
    get_pinata_service = None
# Mozilla Voice integration (optional)
try:
    from mozilla_voice_analyzer_fallback import mozilla_voice_analyzer
    MOZILLA_VOICE_AVAILABLE = True
except ImportError:
    MOZILLA_VOICE_AVAILABLE = False
    mozilla_voice_analyzer = None
import json
from functools import wraps
import base64
import uuid
from datetime import datetime
from email_service import send_call_analysis_notification

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize the scam detector
scam_detector = CompleteScamDetector()

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authorization token is missing'
            }), 401
        
        # Verify token
        user = user_model.verify_jwt_token(token)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Add user to request context
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Scam Detection API is running'
    })

# Authentication endpoints
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate input
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'error': 'Username, email, and password are required'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 6 characters long'
            }), 400
        
        # Create user
        result = user_model.create_user(username, email, password)
        
        if result['success']:
            # Generate JWT token
            token_result = user_model.generate_jwt_token(result['user_id'])
            
            if token_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'User created successfully',
                    'token': token_result['token'],
                    'user': {
                        'id': result['user_id'],
                        'username': username,
                        'email': email
                    }
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': 'User created but failed to generate token'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Signup failed: {str(e)}'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Authenticate user
        auth_result = user_model.authenticate_user(email, password)
        
        if auth_result['success']:
            # Generate JWT token
            token_result = user_model.generate_jwt_token(auth_result['user_id'])
            
            if token_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'token': token_result['token'],
                    'user': {
                        'id': auth_result['user_id'],
                        'username': auth_result['username'],
                        'email': auth_result['email']
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Authentication successful but failed to generate token'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': auth_result['error']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500

@app.route('/api/auth/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile endpoint"""
    try:
        user = request.current_user
        user_data = user_model.get_user_by_id(user['user_id'])
        
        if user_data:
            return jsonify({
                'success': True,
                'user': user_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get profile: {str(e)}'
        }), 500

@app.route('/api/auth/history', methods=['GET'])
@require_auth
def get_call_history():
    """Get user's call history endpoint"""
    try:
        user = request.current_user
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate pagination parameters
        if limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        
        result = user_model.get_user_call_history(
            user['user_id'], 
            limit=limit, 
            offset=offset
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'calls': result['calls'],
                'total_count': result['total_count'],
                'limit': result['limit'],
                'offset': result['offset']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get call history: {str(e)}'
        }), 500

@app.route('/api/auth/statistics', methods=['GET'])
@require_auth
def get_user_statistics():
    """Get user statistics endpoint"""
    try:
        user = request.current_user
        result = user_model.get_user_statistics(user['user_id'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'statistics': result['statistics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get statistics: {str(e)}'
        }), 500

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
            
            # Check for bank-related content and get bank rules
            print("🏦 Checking for bank-related content...")
            bank_analysis = scam_detector.detect_bank_related_content(
                transcription_result['full_text'], 
                []  # We'll extract keywords from the analysis results
            )
            
            bank_rules = ""
            if bank_analysis['is_bank_related']:
                print(f"🏦 Bank-related content detected: {bank_analysis['bank_keywords_detected']}")
                bank_rules = scam_detector.get_bank_rules_from_gemini(
                    transcription_result['full_text'],
                    bank_analysis['bank_keywords_detected']
                )
                print("✅ Bank rules generated")
            else:
                print("ℹ️ No bank-related content detected")
            
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
                    'logic_reason': logic_reason,
                    'bank_analysis': bank_analysis,
                    'bank_rules': bank_rules
                }
            }
            
            # Upload audio to Pinata IPFS
            ipfs_info = None
            if PINATA_AVAILABLE:
                try:
                    print("📤 Uploading audio to Pinata IPFS...")
                    pinata_service = get_pinata_service()
                    
                    # Generate filename with timestamp
                    from datetime import datetime
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    filename = f"audio_analysis_{timestamp}.wav"
                    
                    # Prepare metadata
                    metadata = {
                        "analysis_id": str(uuid.uuid4()),
                        "risk_score": overall_risk_score,
                        "scam_detected": final_scam_detected,
                        "risk_level": risk_level,
                        "speakers_count": len(analysis_results),
                        "keywords_found": len([kw for speaker in analysis_results.values() for kw in speaker.get('scam_keywords', [])])
                    }
                    
                    # Upload the WAV file
                    ipfs_info = pinata_service.upload_audio_file(audio_bytes, filename, metadata)
                    
                    if ipfs_info:
                        print(f"✅ Audio uploaded to IPFS: {ipfs_info['ipfs_hash']}")
                        # Add IPFS info to response
                        response_data['data']['ipfs_hash'] = ipfs_info['ipfs_hash']
                        response_data['data']['ipfs_url'] = ipfs_info['ipfs_url']
                        response_data['data']['pinata_url'] = ipfs_info['pinata_url']
                    else:
                        print("❌ Failed to upload audio to IPFS")
                        
                except Exception as e:
                    print(f"❌ Error uploading to Pinata: {e}")
                    # Continue without IPFS upload
            else:
                print("ℹ️ Pinata not available, skipping IPFS upload")
            
            # Store analysis data in database
            print("🔄 Starting database storage process...")
            try:
                # Get user info if authenticated
                user_id = getattr(request, 'current_user', {}).get('user_id') if hasattr(request, 'current_user') else None
                print(f"🔍 User ID: {user_id}")
                print(f"🔍 Has current_user: {hasattr(request, 'current_user')}")
                
                # Create analysis record in the format expected by save_analyzed_call
                analysis_record = {
                    'analysis_id': str(uuid.uuid4()),
                    'caller': 'Unknown',  # We don't have caller info
                    'transcription': transcription_result,
                    'analysis': analysis_results,  # This is what the method expects
                    'overall_risk_score': overall_risk_score,
                    'risk_level': risk_level,
                    'scam_detected': final_scam_detected,
                    'gemini_suggestion': gemini_suggestion,
                    'logic_scam_detected': logic_scam_detected,
                    'logic_reason': logic_reason,
                    'call_summary': call_summary,
                    'audio_duration': len(audio_bytes) / (16000 * 2) if 'audio_bytes' in locals() else 0,
                    'speakers_count': len(analysis_results),
                    'keywords_found': [keyword for result in analysis_results.values() for keyword in result.get('scam_keywords', [])],
                    'audio_format': 'webm',
                    'ipfs_hash': ipfs_info['ipfs_hash'] if ipfs_info else None,
                    'ipfs_url': ipfs_info['ipfs_url'] if ipfs_info else None,
                    'pinata_url': ipfs_info['pinata_url'] if ipfs_info else None
                }
                
                print(f"🔍 Analysis record created: {analysis_record['analysis_id']}")
                print(f"🔍 Record keys: {list(analysis_record.keys())}")
                print(f"🔍 Transcription text length: {len(transcription_result.get('full_text', ''))}")
                print(f"🔍 Speakers detected: {len(analysis_results)}")
                print(f"🔍 Keywords found: {len(analysis_record['keywords_found'])}")
                
                # Save to analyzed_calls collection
                print("🔄 Calling analyzed_call_model.save_analyzed_call...")
                print(f"🔍 User ID for save: {user_id}")
                print(f"🔍 Analysis record type: {type(analysis_record)}")
                
                # Handle None user_id - pass None to the method
                user_id_str = str(user_id) if user_id else None
                print(f"🔍 User ID for save: {user_id_str}")
                
                save_result = analyzed_call_model.save_analyzed_call(user_id_str, analysis_record)
                print(f"🔍 Save result: {save_result}")
                
                if save_result.get('success'):
                    print("✅ Analysis data stored in database successfully")
                    # Add analysis_id to response
                    response_data['data']['analysis_id'] = analysis_record['analysis_id']
                    
                    # Send email notification if user is authenticated
                    if user_id:
                        try:
                            print("📧 Sending email notification...")
                            # Get user info for email
                            user_info = user_model.get_user_by_id(user_id)
                            if user_info:
                                user_email = user_info.get('email')
                                user_name = user_info.get('username', user_info.get('name', 'User'))
                                
                                if user_email:
                                    # Prepare analysis data for email
                                    email_data = {
                                        'timestamp': analysis_record['timestamp'],
                                        'caller': analysis_record['caller'],
                                        'overall_risk_score': analysis_record['overall_risk_score'],
                                        'scam_detected': analysis_record['scam_detected'],
                                        'keywords_found': analysis_record['keywords_found'],
                                        'transcription': analysis_record.get('transcription', {}),
                                        'call_summary': analysis_record.get('call_summary', '')
                                    }
                                    
                                    # Send email notification
                                    email_sent = send_call_analysis_notification(user_email, user_name, email_data)
                                    if email_sent:
                                        print(f"✅ Email notification sent to {user_email}")
                                    else:
                                        print(f"❌ Failed to send email to {user_email}")
                                else:
                                    print("❌ User email not found, skipping email notification")
                            else:
                                print("❌ User info not found, skipping email notification")
                        except Exception as e:
                            print(f"❌ Error sending email notification: {e}")
                            # Don't fail the request if email fails
                    else:
                        print("ℹ️ No authenticated user, skipping email notification")
                else:
                    print(f"❌ Database save failed: {save_result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"❌ Exception in database storage: {e}")
                import traceback
                print(f"🔍 Full traceback: {traceback.format_exc()}")
                # Continue without failing the request
            
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

@app.route('/api/analyze-with-mozilla', methods=['POST'])
def analyze_with_mozilla():
    """Enhanced analysis using Mozilla Voice pre-trained models"""
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
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Convert WebM to WAV if needed
            wav_file_path = temp_file_path.replace('.wav', '_converted.wav')
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(temp_file_path, format="webm")
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(wav_file_path, format="wav")
                temp_file_path = wav_file_path
            except:
                # Keep original file if conversion fails
                pass
            
            # Run enhanced analysis with Mozilla Voice integration
            print("🔄 Running enhanced analysis with Mozilla Voice...")
            combined_analysis = scam_detector.analyze_conversation_with_mozilla(temp_file_path)
            
            return jsonify({
                'success': True,
                'data': combined_analysis
            })
            
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

def calculate_combined_risk(existing_analysis, mozilla_insights):
    """Calculate combined risk score from both analyses"""
    try:
        # Get existing risk score
        existing_risk = existing_analysis.get('overall_risk_score', 0.5)
        
        # Get Mozilla Voice risk score
        mozilla_risk = mozilla_insights.get('overall_assessment', {}).get('overall_risk_score', 0.5)
        
        # Combine with weights (you can adjust these)
        combined_risk = (existing_risk * 0.6) + (mozilla_risk * 0.4)
        
        return {
            'combined_score': combined_risk,
            'existing_score': existing_risk,
            'mozilla_score': mozilla_risk,
            'risk_level': 'high' if combined_risk > 0.7 else 'medium' if combined_risk > 0.4 else 'low'
        }
    except Exception as e:
        print(f"❌ Error calculating combined risk: {e}")
        return {'combined_score': 0.5, 'risk_level': 'medium'}

def generate_enhanced_suggestions(existing_analysis, mozilla_insights):
    """Generate enhanced suggestions combining both analyses"""
    suggestions = []
    
    try:
        # Add existing suggestions
        if existing_analysis.get('gemini_suggestion'):
            suggestions.append(f"🤖 AI Analysis: {existing_analysis['gemini_suggestion']}")
        
        # Add Mozilla Voice recommendations
        mozilla_recommendations = mozilla_insights.get('recommendations', [])
        for rec in mozilla_recommendations:
            suggestions.append(f"🎤 Voice Analysis: {rec}")
        
        # Add combined assessment
        overall_assessment = mozilla_insights.get('overall_assessment', {})
        if overall_assessment.get('assessment'):
            suggestions.append(f"📊 Overall Assessment: {overall_assessment['assessment']}")
        
        return suggestions
        
    except Exception as e:
        print(f"❌ Error generating enhanced suggestions: {e}")
        return ["Analysis completed with some limitations"]

@app.route('/api/analyzed-calls', methods=['GET'])
def get_analyzed_calls():
    """Get analysis history for the authenticated user"""
    print("🔍 API: /api/analyzed-calls called")
    try:
        # Get user info if authenticated
        user_id = getattr(request, 'current_user', {}).get('user_id') if hasattr(request, 'current_user') else None
        print(f"🔍 User ID: {user_id}")
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        print(f"🔍 Query params - limit: {limit}, offset: {offset}")
        
        # Get analyzed calls from database
        print("🔄 Fetching calls from database...")
        calls = analyzed_call_model.get_analyzed_calls(user_id, limit, offset)
        print(f"🔍 Retrieved {len(calls)} calls from database")
        
        if calls:
            print(f"🔍 Sample call keys: {list(calls[0].keys())}")
            print(f"🔍 Sample call timestamp: {calls[0].get('timestamp')}")
            print(f"🔍 Sample call caller: {calls[0].get('caller')}")
            print(f"🔍 Sample call probability: {calls[0].get('probability')}")
            print(f"🔍 Sample call keywords: {calls[0].get('keywords')}")
            print(f"🔍 Sample call keywords_found: {calls[0].get('keywords_found')}")
            print(f"🔍 Sample call scam_detected: {calls[0].get('scam_detected')}")
            print(f"🔍 Sample call overall_risk_score: {calls[0].get('overall_risk_score')}")
            print(f"🔍 Sample call transcription: {calls[0].get('transcription')}")
            print(f"🔍 Sample call outcome: {calls[0].get('outcome')}")
            print(f"🔍 Sample call risk_level: {calls[0].get('risk_level')}")
            print(f"🔍 Sample call call_summary: {calls[0].get('call_summary')}")
        
        response_data = {
            'success': True,
            'data': calls,
            'total': len(calls),
            'limit': limit,
            'offset': offset
        }
        
        print(f"🔍 Response data keys: {list(response_data.keys())}")
        print(f"🔍 Response data length: {len(response_data['data'])}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in get_analyzed_calls: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyzed-calls/<analysis_id>', methods=['GET'])
def get_analyzed_call_details(analysis_id):
    """Get detailed analysis for a specific call"""
    try:
        # Get user info if authenticated
        user_id = getattr(request, 'current_user', {}).get('user_id') if hasattr(request, 'current_user') else None
        
        # Get specific analyzed call
        call = analyzed_call_model.get_analyzed_call_by_id(analysis_id, user_id)
        
        if not call:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': call
        })
        
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
        'high_risk_phrases': scam_detector.high_risk_phrases[:3],  # Show first 3 phrases
        'mozilla_voice_available': MOZILLA_VOICE_AVAILABLE
    })

if __name__ == '__main__':
    print("🚀 Starting Scam Detection API...")
    print("📡 API will be available at: http://localhost:5000")
    print("🔗 Frontend should connect to: http://localhost:5000/api/analyze-audio")
    print("⏱️  Timeout settings: 60 seconds for audio processing")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)


