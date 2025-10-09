import os
import jwt
import hashlib
from datetime import datetime, timedelta
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    def __init__(self):
        """Initialize MongoDB connection"""
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is required")
        
        # Add SSL configuration for MongoDB Atlas
        import ssl
        self.client = MongoClient(
            mongodb_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            retryWrites=True,
            w='majority',
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000
        )
        self.db = self.client['voice_scam_detector']
        self.users_collection = self.db['users']
        
        # Test connection before creating indexes
        try:
            self.client.admin.command('ping')
            print("✅ MongoDB connection successful")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
        
        # Create indexes for better performance
        try:
            self.users_collection.create_index("email", unique=True)
            self.users_collection.create_index("username", unique=True)
            print("✅ MongoDB indexes created successfully")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
            # Continue without indexes if they already exist
    
    def create_user(self, username, email, password):
        """Create a new user"""
        try:
            # Check if user already exists
            if self.users_collection.find_one({"email": email}):
                return {
                    'success': False,
                    'error': 'User with this email already exists'
                }
            
            if self.users_collection.find_one({"username": username}):
                return {
                    'success': False,
                    'error': 'Username already taken'
                }
            
            # Hash password
            password_hash = generate_password_hash(password)
            
            # Create user document
            user_doc = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'created_at': datetime.utcnow(),
                'last_login': None,
                'call_history': [],
                'total_calls': 0,
                'scam_calls_detected': 0
            }
            
            # Insert user
            result = self.users_collection.insert_one(user_doc)
            
            if result.inserted_id:
                return {
                    'success': True,
                    'user_id': str(result.inserted_id),
                    'message': 'User created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create user'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating user: {str(e)}'
            }
    
    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        try:
            user = self.users_collection.find_one({"email": email})
            
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            # Check password
            if not check_password_hash(user['password_hash'], password):
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            # Update last login
            self.users_collection.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            return {
                'success': True,
                'user_id': str(user['_id']),
                'username': user['username'],
                'email': user['email']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error authenticating user: {str(e)}'
            }
    
    def generate_jwt_token(self, user_id):
        """Generate JWT token for user"""
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
                'iat': datetime.utcnow()
            }
            
            jwt_secret = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
            token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            
            return {
                'success': True,
                'token': token
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generating token: {str(e)}'
            }
    
    def verify_jwt_token(self, token):
        """Verify JWT token and return user data"""
        try:
            jwt_secret = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            
            user_id = payload['user_id']
            user = self.users_collection.find_one({"_id": user_id})
            
            if not user:
                return None
            
            return {
                'user_id': str(user['_id']),
                'username': user['username'],
                'email': user['email']
            }
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            from bson import ObjectId
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                return None
            
            # Remove password hash from response
            user['_id'] = str(user['_id'])
            del user['password_hash']
            
            return user
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def save_call_history(self, user_id, call_data):
        """Save call history for user"""
        try:
            from bson import ObjectId
            
            call_entry = {
                'timestamp': datetime.utcnow(),
                'audio_duration': call_data.get('audio_duration', 0),
                'speakers_count': call_data.get('speakers_count', 0),
                'scam_detected': call_data.get('scam_detected', False),
                'risk_level': call_data.get('risk_level', 'low'),
                'overall_risk_score': call_data.get('overall_risk_score', 0),
                'call_summary': call_data.get('call_summary', ''),
                'gemini_suggestion': call_data.get('gemini_suggestion', ''),
                'transcription': call_data.get('transcription', {}),
                'analysis': call_data.get('analysis', {}),
                'ip_address': call_data.get('ip_address', ''),
                'user_agent': call_data.get('user_agent', ''),
                'audio_format': call_data.get('audio_format', 'webm'),
                'caller': call_data.get('caller', 'Unknown')
            }
            
            # Add to user's call history
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$push": {"call_history": call_entry},
                    "$inc": {"total_calls": 1}
                }
            )
            
            if result.modified_count > 0:
                # Update scam calls count if scam detected
                if call_data.get('scam_detected', False):
                    self.users_collection.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$inc": {"scam_calls_detected": 1}}
                    )
                
                return {
                    'success': True,
                    'call_id': str(call_entry['timestamp']),
                    'message': 'Call history saved successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save call history'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error saving call history: {str(e)}'
            }
    
    def get_user_call_history(self, user_id, limit=50, offset=0):
        """Get user's call history with pagination"""
        try:
            from bson import ObjectId
            
            user = self.users_collection.find_one(
                {"_id": ObjectId(user_id)},
                {"call_history": 1, "total_calls": 1}
            )
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            call_history = user.get('call_history', [])
            total_count = len(call_history)
            
            # Sort by timestamp (newest first) and apply pagination
            sorted_calls = sorted(call_history, key=lambda x: x['timestamp'], reverse=True)
            paginated_calls = sorted_calls[offset:offset + limit]
            
            return {
                'success': True,
                'calls': paginated_calls,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting call history: {str(e)}'
            }
    
    def get_user_statistics(self, user_id):
        """Get user statistics"""
        try:
            from bson import ObjectId
            
            user = self.users_collection.find_one(
                {"_id": ObjectId(user_id)},
                {"total_calls": 1, "scam_calls_detected": 1, "call_history": 1}
            )
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            total_calls = user.get('total_calls', 0)
            scam_calls = user.get('scam_calls_detected', 0)
            call_history = user.get('call_history', [])
            
            # Calculate additional statistics
            safe_calls = total_calls - scam_calls
            scam_percentage = (scam_calls / total_calls * 100) if total_calls > 0 else 0
            
            # Calculate average risk score
            risk_scores = [call.get('overall_risk_score', 0) for call in call_history]
            avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            statistics = {
                'total_calls': total_calls,
                'scam_calls_detected': scam_calls,
                'safe_calls': safe_calls,
                'scam_percentage': round(scam_percentage, 2),
                'average_risk_score': round(avg_risk_score, 2),
                'last_call_date': call_history[0]['timestamp'] if call_history else None
            }
            
            return {
                'success': True,
                'statistics': statistics
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting statistics: {str(e)}'
            }

# Create global instance
user_model = UserModel()