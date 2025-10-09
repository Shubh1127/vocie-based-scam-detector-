import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AnalyzedCallModel:
    def __init__(self):
        """Initialize MongoDB connection and analyzed calls collection"""
        self.mongodb_url = os.getenv('MONGODB_URI')
        if not self.mongodb_url:
            raise ValueError("MONGODB_URI environment variable is required")
        
        try:
            # Add SSL configuration for MongoDB Atlas
            import ssl
            self.client = MongoClient(
                self.mongodb_url,
                tls=True,
                tlsAllowInvalidCertificates=True,
                retryWrites=True,
                w='majority',
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000
            )
            self.db = self.client['voice_scam_detector']
            self.analyzed_calls_collection = self.db['analyzed_calls']
            
            # Test connection before creating indexes
            self.client.admin.command('ping')
            print("✅ AnalyzedCallModel MongoDB connection successful")
            
            # Create indexes for better performance
            self.analyzed_calls_collection.create_index("user_id")
            self.analyzed_calls_collection.create_index("timestamp")
            self.analyzed_calls_collection.create_index("probability")
            self.analyzed_calls_collection.create_index("outcome")
            self.analyzed_calls_collection.create_index([("user_id", 1), ("timestamp", -1)])
            print("✅ AnalyzedCallModel indexes created successfully")
            
            print("✅ AnalyzedCall MongoDB connection established successfully")
            
        except ConnectionFailure as e:
            print(f"❌ AnalyzedCall MongoDB connection failed: {e}")
            raise
    
    def save_analyzed_call(self, user_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save analyzed call data
        
        Args:
            user_id: User's MongoDB ObjectId as string
            call_data: Dictionary containing call analysis data
            
        Returns:
            Dict with success status and call ID
        """
        try:
            print(f"🔍 DEBUG: AnalyzedCallModel.save_analyzed_call called")
            print(f"🔍 DEBUG: User ID: {user_id}")
            print(f"🔍 DEBUG: Call data keys: {list(call_data.keys())}")
            
            # Extract keywords from analysis
            keywords = []
            if 'analysis' in call_data:
                print(f"🔍 DEBUG: Analysis data found, extracting keywords...")
                for speaker_data in call_data['analysis'].values():
                    if 'scam_keywords' in speaker_data:
                        keywords.extend(speaker_data['scam_keywords'])
                        print(f"🔍 DEBUG: Found keywords from speaker: {speaker_data['scam_keywords']}")
            
            # Remove duplicates and filter out phrase markers
            keywords = list(set([kw for kw in keywords if not kw.startswith('[PHRASE:')]))
            print(f"🔍 DEBUG: Final keywords: {keywords}")
            
            # Determine outcome based on risk level and scam detection
            scam_detected = call_data.get('scam_detected', False)
            risk_level = call_data.get('risk_level', 'safe')
            overall_risk_score = call_data.get('overall_risk_score', 0.0)
            
            # Convert risk score to probability percentage
            probability = int(overall_risk_score * 100)
            
            # Determine outcome
            if scam_detected or risk_level == 'critical':
                outcome = 'alerted'
            elif risk_level in ['high', 'medium'] or probability >= 40:
                outcome = 'potential_risk'
            else:
                outcome = 'safe'
            
            print(f"🔍 DEBUG: Calculated values:")
            print(f"   - Scam detected: {scam_detected}")
            print(f"   - Risk level: {risk_level}")
            print(f"   - Overall risk score: {overall_risk_score}")
            print(f"   - Probability: {probability}")
            print(f"   - Outcome: {outcome}")
            
            # Prepare analyzed call document
            analyzed_call_doc = {
                "user_id": ObjectId(user_id),
                "timestamp": datetime.utcnow(),
                "caller": call_data.get('caller', 'Unknown'),
                "probability": probability,
                "keywords": keywords,
                "outcome": outcome,
                "risk_level": risk_level,
                "scam_detected": scam_detected,
                "overall_risk_score": overall_risk_score,
                "call_summary": call_data.get('call_summary', ''),
                "gemini_suggestion": call_data.get('gemini_suggestion', ''),
                "transcription": {
                    "full_text": call_data.get('transcription', {}).get('full_text', ''),
                    "speaker_count": call_data.get('speakers_count', 0)
                },
                "analysis": call_data.get('analysis', {}),
                "metadata": {
                    "audio_duration": call_data.get('audio_duration', 0),
                    "ip_address": call_data.get('ip_address'),
                    "user_agent": call_data.get('user_agent'),
                    "audio_format": call_data.get('audio_format', 'webm')
                }
            }
            
            print(f"🔍 DEBUG: Prepared document for insertion")
            print(f"🔍 DEBUG: Document keys: {list(analyzed_call_doc.keys())}")
            
            # Insert analyzed call
            print(f"🔍 DEBUG: Attempting to insert document into MongoDB...")
            result = self.analyzed_calls_collection.insert_one(analyzed_call_doc)
            call_id = str(result.inserted_id)
            
            print(f"✅ DEBUG: Document inserted successfully with ID: {call_id}")
            
            return {
                "success": True,
                "call_id": call_id,
                "message": "Analyzed call saved successfully"
            }
            
        except Exception as e:
            print(f"❌ ERROR in save_analyzed_call: {e}")
            print(f"❌ ERROR type: {type(e)}")
            import traceback
            print(f"❌ ERROR traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Failed to save analyzed call: {str(e)}"
            }
    
    def get_user_analyzed_calls(self, user_id: str, limit: int = 50, offset: int = 0, 
                               risk_filter: str = 'all') -> Dict[str, Any]:
        """
        Get analyzed calls for a user with filtering
        
        Args:
            user_id: User's MongoDB ObjectId as string
            limit: Maximum number of calls to return
            offset: Number of calls to skip
            risk_filter: Filter by risk level ('all', 'high', 'medium', 'low')
            
        Returns:
            Dict with analyzed calls data
        """
        try:
            # Build query filter
            query_filter = {"user_id": ObjectId(user_id)}
            
            # Add risk filter
            if risk_filter != 'all':
                if risk_filter == 'high':
                    query_filter["probability"] = {"$gte": 75}
                elif risk_filter == 'medium':
                    query_filter["probability"] = {"$gte": 40, "$lt": 75}
                elif risk_filter == 'low':
                    query_filter["probability"] = {"$lt": 40}
            
            # Get total count
            total_count = self.analyzed_calls_collection.count_documents(query_filter)
            
            # Get analyzed calls with pagination
            calls = list(self.analyzed_calls_collection.find(query_filter)
                        .sort("timestamp", -1)
                        .skip(offset)
                        .limit(limit))
            
            # Format calls data
            formatted_calls = []
            for call in calls:
                formatted_call = {
                    "id": str(call["_id"]),
                    "time": call["timestamp"].isoformat(),
                    "caller": call.get("caller", "Unknown"),
                    "probability": call.get("probability", 0),
                    "keywords": call.get("keywords", []),
                    "outcome": call.get("outcome", "safe"),
                    "risk_level": call.get("risk_level", "safe"),
                    "scam_detected": call.get("scam_detected", False),
                    "call_summary": call.get("call_summary", ""),
                    "transcription": call.get("transcription", {}),
                    "metadata": call.get("metadata", {})
                }
                formatted_calls.append(formatted_call)
            
            return {
                "success": True,
                "calls": formatted_calls,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get analyzed calls: {str(e)}"
            }
    
    def get_user_call_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get call statistics for a user
        
        Args:
            user_id: User's MongoDB ObjectId as string
            
        Returns:
            Dict with call statistics
        """
        try:
            # Get total calls
            total_calls = self.analyzed_calls_collection.count_documents({"user_id": ObjectId(user_id)})
            
            # Get scam calls
            scam_calls = self.analyzed_calls_collection.count_documents({
                "user_id": ObjectId(user_id),
                "scam_detected": True
            })
            
            # Get calls by outcome
            alerted_calls = self.analyzed_calls_collection.count_documents({
                "user_id": ObjectId(user_id),
                "outcome": "alerted"
            })
            
            potential_risk_calls = self.analyzed_calls_collection.count_documents({
                "user_id": ObjectId(user_id),
                "outcome": "potential_risk"
            })
            
            safe_calls = self.analyzed_calls_collection.count_documents({
                "user_id": ObjectId(user_id),
                "outcome": "safe"
            })
            
            # Get recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow().replace(day=1)  # Simplified: first day of current month
            recent_calls = self.analyzed_calls_collection.count_documents({
                "user_id": ObjectId(user_id),
                "timestamp": {"$gte": thirty_days_ago}
            })
            
            # Calculate scam detection rate
            scam_rate = (scam_calls / total_calls * 100) if total_calls > 0 else 0
            
            return {
                "success": True,
                "statistics": {
                    "total_calls": total_calls,
                    "scam_calls": scam_calls,
                    "safe_calls": safe_calls,
                    "alerted_calls": alerted_calls,
                    "potential_risk_calls": potential_risk_calls,
                    "scam_detection_rate": round(scam_rate, 2),
                    "recent_calls": recent_calls
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get call statistics: {str(e)}"
            }
    
    def search_calls(self, user_id: str, search_query: str, limit: int = 50) -> Dict[str, Any]:
        """
        Search analyzed calls by caller or keywords
        
        Args:
            user_id: User's MongoDB ObjectId as string
            search_query: Search query string
            limit: Maximum number of results
            
        Returns:
            Dict with search results
        """
        try:
            # Build search query
            search_filter = {
                "user_id": ObjectId(user_id),
                "$or": [
                    {"caller": {"$regex": search_query, "$options": "i"}},
                    {"keywords": {"$regex": search_query, "$options": "i"}},
                    {"call_summary": {"$regex": search_query, "$options": "i"}}
                ]
            }
            
            # Get search results
            calls = list(self.analyzed_calls_collection.find(search_filter)
                        .sort("timestamp", -1)
                        .limit(limit))
            
            # Format results
            formatted_calls = []
            for call in calls:
                formatted_call = {
                    "id": str(call["_id"]),
                    "time": call["timestamp"].isoformat(),
                    "caller": call.get("caller", "Unknown"),
                    "probability": call.get("probability", 0),
                    "keywords": call.get("keywords", []),
                    "outcome": call.get("outcome", "safe"),
                    "risk_level": call.get("risk_level", "safe"),
                    "scam_detected": call.get("scam_detected", False),
                    "call_summary": call.get("call_summary", "")
                }
                formatted_calls.append(formatted_call)
            
            return {
                "success": True,
                "calls": formatted_calls,
                "total_count": len(formatted_calls),
                "search_query": search_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search calls: {str(e)}"
            }
    
    def delete_analyzed_call(self, user_id: str, call_id: str) -> Dict[str, Any]:
        """
        Delete an analyzed call
        
        Args:
            user_id: User's MongoDB ObjectId as string
            call_id: Call's MongoDB ObjectId as string
            
        Returns:
            Dict with success status
        """
        try:
            result = self.analyzed_calls_collection.delete_one({
                "_id": ObjectId(call_id),
                "user_id": ObjectId(user_id)
            })
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Analyzed call deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Call not found or access denied"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete analyzed call: {str(e)}"
            }
    
    def close_connection(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            print("✅ AnalyzedCall MongoDB connection closed")

# Global instance
analyzed_call_model = AnalyzedCallModel()

