"""
Enhanced Face Recognition Service for University System
"""

import cv2
import numpy as np
import face_recognition
import pickle
import os
import logging
from typing import Dict, Any, Optional, List
from io import BytesIO
from PIL import Image
import json
import base64

logger = logging.getLogger(__name__)

class FaceRecognitionService:
    """Enhanced face recognition service for university attendance"""
    
    def __init__(self):
        self.model_path = "models/svm_model_160x160.pkl"
        self.embeddings_path = "models/faces_embeddings_done_35classes.npz"
        self.confidence_threshold = 0.85
        self.verification_threshold = 0.80
        self.known_faces = {}
        self.face_classifier = None
        self.label_encoder = None
        
    async def initialize(self):
        """Initialize face recognition models"""
        try:
            self.load_models()
            logger.info("✅ Face recognition service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize face recognition: {e}")
            
    def load_models(self):
        """Load face recognition models"""
        try:
            # Load SVM model if exists
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    if isinstance(model_data, dict):
                        self.face_classifier = model_data.get('classifier')
                        self.label_encoder = model_data.get('label_encoder')
                    else:
                        # Assume it's just the classifier
                        self.face_classifier = model_data
                        self.label_encoder = None  # or load separately if needed
                logger.info("✅ SVM model loaded")
            
            # Load face embeddings if exists
            if os.path.exists(self.embeddings_path):
                embeddings_data = np.load(self.embeddings_path)
                self.known_faces = {
                    'embeddings': embeddings_data['arr_0'],
                    'labels': embeddings_data['arr_1']
                }
                logger.info("✅ Face embeddings loaded")
                
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process uploaded image for face recognition"""
        try:
            # Convert bytes to image
            image = Image.open(BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert to RGB if needed
            if len(image_array.shape) == 3 and image_array.shape[2] == 4:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            elif len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(image_array)
            
            if not face_locations:
                return {
                    "success": False,
                    "error": "No face detected in the image"
                }
            
            if len(face_locations) > 1:
                return {
                    "success": False,
                    "error": "Multiple faces detected. Please ensure only one face is visible"
                }
            
            # Extract face encoding
            face_encodings = face_recognition.face_encodings(image_array, face_locations)
            
            if not face_encodings:
                return {
                    "success": False,
                    "error": "Could not extract face features"
                }
            
            face_encoding = face_encodings[0]
            
            # Recognize face if models are loaded
            recognition_result = self.recognize_face(face_encoding)
            
            return {
                "success": True,
                "face_encoding": face_encoding.tolist(),
                "face_location": face_locations[0],
                "recognition": recognition_result
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing image: {e}")
            return {
                "success": False,
                "error": f"Error processing image: {str(e)}"
            }
    
    def recognize_face(self, face_encoding: np.ndarray) -> Dict[str, Any]:
        """Recognize face using loaded models"""
        try:
            # If no models loaded, return unrecognized
            if not self.known_faces or not self.face_classifier:
                return {
                    "recognized": False,
                    "confidence": 0.0,
                    "user_id": None,
                    "name": "Unknown"
                }
            
            # Compare with known faces
            known_encodings = self.known_faces['embeddings']
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            # Find best match
            min_distance_index = np.argmin(distances)
            min_distance = distances[min_distance_index]
            confidence = 1 - min_distance
            
            if confidence >= self.confidence_threshold:
                label = self.known_faces['labels'][min_distance_index]
                return {
                    "recognized": True,
                    "confidence": float(confidence),
                    "user_id": int(label) if str(label).isdigit() else None,
                    "name": str(label)
                }
            else:
                return {
                    "recognized": False,
                    "confidence": float(confidence),
                    "user_id": None,
                    "name": "Unknown"
                }
                
        except Exception as e:
            logger.error(f"❌ Error recognizing face: {e}")
            return {
                "recognized": False,
                "confidence": 0.0,
                "user_id": None,
                "name": "Unknown",
                "error": str(e)
            }
    
    def verify_face_against_user(self, image_data: bytes, stored_encoding: str) -> Dict[str, Any]:
        """Verify face against stored user encoding"""
        try:
            # Process new image
            result = self.process_image(image_data)
            
            if not result["success"]:
                return result
            
            new_encoding = np.array(result["face_encoding"])
            
            # Parse stored encoding
            if isinstance(stored_encoding, str):
                try:
                    stored_encoding_array = np.array(json.loads(stored_encoding))
                except:
                    return {
                        "success": False,
                        "error": "Invalid stored face encoding"
                    }
            else:
                stored_encoding_array = np.array(stored_encoding)
            
            # Compare encodings
            distance = face_recognition.face_distance([stored_encoding_array], new_encoding)[0]
            confidence = 1 - distance
            is_match = confidence >= self.verification_threshold
            
            return {
                "success": True,
                "is_match": is_match,
                "confidence": float(confidence),
                "threshold": self.verification_threshold
            }
            
        except Exception as e:
            logger.error(f"❌ Error verifying face: {e}")
            return {
                "success": False,
                "error": f"Face verification failed: {str(e)}"
            }
    
    def register_face(self, image_data: bytes, user_id: int) -> Dict[str, Any]:
        """Register face for a new user"""
        try:
            # Process image
            result = self.process_image(image_data)
            
            if not result["success"]:
                return result
            
            face_encoding = result["face_encoding"]
            
            # Save face image
            image_filename = f"face_{user_id}_{int(datetime.now().timestamp())}.jpg"
            image_path = os.path.join("uploads/faces", image_filename)
            
            # Create directory if not exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Save image
            image = Image.open(BytesIO(image_data))
            image.save(image_path)
            
            return {
                "success": True,
                "encoding": json.dumps(face_encoding),
                "image_path": image_path,
                "confidence": 1.0
            }
            
        except Exception as e:
            logger.error(f"❌ Error registering face: {e}")
            return {
                "success": False,
                "error": f"Face registration failed: {str(e)}"
            }
    
    def identify_student(self, image_data: bytes) -> Dict[str, Any]:
        """Identify student from image (for lecturer use)"""
        try:
            # Process image
            result = self.process_image(image_data)
            
            if not result["success"]:
                return result
            
            recognition = result["recognition"]
            
            if recognition["recognized"] and recognition["user_id"]:
                return {
                    "success": True,
                    "recognized": True,
                    "user_id": recognition["user_id"],
                    "confidence": recognition["confidence"]
                }
            else:
                return {
                    "success": True,
                    "recognized": False,
                    "user_id": None,
                    "confidence": recognition["confidence"]
                }
                
        except Exception as e:
            logger.error(f"❌ Error identifying student: {e}")
            return {
                "success": False,
                "error": f"Student identification failed: {str(e)}"
            }

# Create global instance
face_recognition_service = FaceRecognitionService()