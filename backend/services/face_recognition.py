"""
Face Recognition Service
Integrates with your existing facial recognition system
"""

import cv2 as cv
import numpy as np
import pickle
import os
import json
import logging
from typing import Optional, Dict, Tuple, List
from datetime import datetime
from pathlib import Path

# Your existing imports
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class FaceRecognitionService:
    """
    Face Recognition Service that integrates with your existing system
    """
    
    def __init__(self):
        self.facenet = None
        self.face_embeddings = None
        self.encoder = None
        self.haarcascade = None
        self.model = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the face recognition models"""
        try:
            logger.info("🔄 Initializing Face Recognition Service...")
            
            # Initialize FaceNet
            self.facenet = FaceNet()
            logger.info("✅ FaceNet model loaded")
            
            # Load face embeddings
            embeddings_path = Path(settings.EMBEDDINGS_PATH)
            if embeddings_path.exists():
                self.face_embeddings = np.load(str(embeddings_path))
                Y = self.face_embeddings['arr_1']
                
                # Initialize label encoder
                self.encoder = LabelEncoder()
                self.encoder.fit(Y)
                logger.info("✅ Face embeddings and encoder loaded")
            else:
                logger.warning(f"⚠️ Face embeddings not found at {embeddings_path}")
            
            # Load Haar Cascade
            cascade_path = Path(settings.HAARCASCADE_PATH)
            if cascade_path.exists():
                self.haarcascade = cv.CascadeClassifier(str(cascade_path))
                logger.info("✅ Haar Cascade loaded")
            else:
                # Try default OpenCV path
                self.haarcascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
                logger.info("✅ Default Haar Cascade loaded")
            
            # Load SVM model
            model_path = Path(settings.MODEL_PATH)
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("✅ SVC model loaded")
            else:
                logger.warning(f"⚠️ SVC model not found at {model_path}")
            
            self.is_initialized = True
            logger.info("🎉 Face Recognition Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Face Recognition Service: {e}")
            raise
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image
        Returns list of face bounding boxes (x, y, w, h)
        """
        if not self.is_initialized:
            raise RuntimeError("Face recognition service not initialized")
        
        try:
            # Convert to grayscale for detection
            gray_img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.haarcascade.detectMultiScale(
                gray_img, 
                scaleFactor=1.3, 
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return [(x, y, w, h) for x, y, w, h in faces]
            
        except Exception as e:
            logger.error(f"❌ Error detecting faces: {e}")
            return []
    
    def extract_face_embedding(self, image: np.ndarray, face_box: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Extract face embedding from detected face
        """
        if not self.is_initialized:
            raise RuntimeError("Face recognition service not initialized")
        
        try:
            x, y, w, h = face_box
            
            # Extract face region
            face_img = image[y:y+h, x:x+w]
            
            # Resize to 160x160 (FaceNet input size)
            face_img = cv.resize(face_img, (160, 160))
            
            # Convert BGR to RGB
            face_img = cv.cvtColor(face_img, cv.COLOR_BGR2RGB)
            
            # Add batch dimension
            face_img = np.expand_dims(face_img, axis=0)
            
            # Extract embedding
            embedding = self.facenet.embeddings(face_img)
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Error extracting face embedding: {e}")
            return None
    
    def recognize_face(self, embedding: np.ndarray) -> Dict:
        """
        Recognize face from embedding
        Returns recognition result with confidence
        """
        if not self.is_initialized or self.model is None:
            raise RuntimeError("Face recognition service not initialized or model not loaded")
        
        try:
            # Predict using SVM model
            prediction = self.model.predict(embedding)
            prediction_proba = self.model.predict_proba(embedding)
            
            # Get confidence score
            confidence = np.max(prediction_proba)
            
            # Get predicted name
            predicted_name = self.encoder.inverse_transform(prediction)[0]
            
            # Check if confidence meets threshold
            is_recognized = confidence >= settings.FACE_CONFIDENCE_THRESHOLD
            
            result = {
                "recognized": is_recognized,
                "name": predicted_name if is_recognized else "Unknown",
                "confidence": float(confidence),
                "threshold": settings.FACE_CONFIDENCE_THRESHOLD,
                "raw_prediction": int(prediction[0]),
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error recognizing face: {e}")
            return {
                "recognized": False,
                "name": "Error",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_image(self, image_data: bytes) -> Dict:
        """
        Process uploaded image for face recognition
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv.imdecode(nparr, cv.IMREAD_COLOR)
            
            if image is None:
                return {
                    "success": False,
                    "error": "Invalid image data",
                    "faces_detected": 0
                }
            
            # Detect faces
            faces = self.detect_faces(image)
            
            if not faces:
                return {
                    "success": False,
                    "error": "No faces detected in image",
                    "faces_detected": 0,
                    "image_shape": image.shape
                }
            
            # Process the first (largest) face
            largest_face = max(faces, key=lambda face: face[2] * face[3])
            
            # Extract embedding
            embedding = self.extract_face_embedding(image, largest_face)
            
            if embedding is None:
                return {
                    "success": False,
                    "error": "Failed to extract face embedding",
                    "faces_detected": len(faces)
                }
            
            # Recognize face
            recognition_result = self.recognize_face(embedding)
            
            return {
                "success": True,
                "faces_detected": len(faces),
                "face_box": largest_face,
                "image_shape": image.shape,
                "recognition": recognition_result
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing image: {e}")
            return {
                "success": False,
                "error": str(e),
                "faces_detected": 0
            }
    
    def process_webcam_frame(self, frame: np.ndarray) -> Dict:
        """
        Process webcam frame for real-time recognition
        """
        try:
            # Detect faces
            faces = self.detect_faces(frame)
            
            results = []
            
            for face_box in faces:
                # Extract embedding
                embedding = self.extract_face_embedding(frame, face_box)
                
                if embedding is not None:
                    # Recognize face
                    recognition = self.recognize_face(embedding)
                    
                    results.append({
                        "face_box": face_box,
                        "recognition": recognition
                    })
            
            return {
                "success": True,
                "faces_detected": len(faces),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing webcam frame: {e}")
            return {
                "success": False,
                "error": str(e),
                "faces_detected": 0
            }
    
    def save_face_encoding(self, user_id: int, image_data: bytes) -> Dict:
        """
        Save face encoding for a user
        """
        try:
            # Process image
            result = self.process_image(image_data)
            
            if not result["success"]:
                return result
            
            # Get the embedding
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv.imdecode(nparr, cv.IMREAD_COLOR)
            face_box = result["face_box"]
            embedding = self.extract_face_embedding(image, face_box)
            
            if embedding is None:
                return {
                    "success": False,
                    "error": "Failed to extract face embedding"
                }
            
            # Convert embedding to JSON-serializable format
            embedding_json = json.dumps(embedding.tolist())
            
            # Save face image
            face_image_path = f"uploads/faces/user_{user_id}_{datetime.now().timestamp()}.jpg"
            os.makedirs(os.path.dirname(face_image_path), exist_ok=True)
            
            x, y, w, h = face_box
            face_img = image[y:y+h, x:x+w]
            cv.imwrite(face_image_path, face_img)
            
            return {
                "success": True,
                "face_encoding": embedding_json,
                "face_image_path": face_image_path,
                "confidence_threshold": settings.FACE_CONFIDENCE_THRESHOLD
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving face encoding: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_face_against_user(self, image_data: bytes, user_face_encoding: str) -> Dict:
        """
        Verify uploaded face against stored user encoding
        """
        try:
            # Process uploaded image
            result = self.process_image(image_data)
            
            if not result["success"]:
                return result
            
            # Get embedding from uploaded image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv.imdecode(nparr, cv.IMREAD_COLOR)
            face_box = result["face_box"]
            new_embedding = self.extract_face_embedding(image, face_box)
            
            if new_embedding is None:
                return {
                    "success": False,
                    "error": "Failed to extract face embedding from uploaded image"
                }
            
            # Load stored embedding
            stored_embedding = np.array(json.loads(user_face_encoding))
            
            # Calculate similarity (using cosine similarity)
            similarity = self.calculate_face_similarity(new_embedding[0], stored_embedding[0])
            
            # Convert similarity to confidence (similarity ranges from -1 to 1)
            confidence = (similarity + 1) / 2
            
            is_match = confidence >= settings.FACE_CONFIDENCE_THRESHOLD
            
            return {
                "success": True,
                "is_match": is_match,
                "confidence": float(confidence),
                "similarity": float(similarity),
                "threshold": settings.FACE_CONFIDENCE_THRESHOLD
            }
            
        except Exception as e:
            logger.error(f"❌ Error verifying face: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_face_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two face embeddings
        """
        try:
            # Normalize embeddings
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def get_face_recognition_stats(self) -> Dict:
        """
        Get face recognition system statistics
        """
        try:
            stats = {
                "is_initialized": self.is_initialized,
                "models_loaded": {
                    "facenet": self.facenet is not None,
                    "haarcascade": self.haarcascade is not None,
                    "svc_model": self.model is not None,
                    "embeddings": self.face_embeddings is not None,
                    "encoder": self.encoder is not None
                },
                "settings": {
                    "confidence_threshold": settings.FACE_CONFIDENCE_THRESHOLD,
                    "max_detection_time": settings.MAX_FACE_DETECTION_TIME,
                    "model_paths": {
                        "svc_model": settings.MODEL_PATH,
                        "embeddings": settings.EMBEDDINGS_PATH,
                        "haarcascade": settings.HAARCASCADE_PATH
                    }
                }
            }
            
            if self.face_embeddings is not None:
                stats["embedding_info"] = {
                    "total_classes": len(self.encoder.classes_) if self.encoder else 0,
                    "embedding_shape": self.face_embeddings['arr_0'].shape if 'arr_0' in self.face_embeddings else None
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {
                "is_initialized": False,
                "error": str(e)
            }
    
    def update_model_with_new_face(self, user_id: int, name: str, face_encoding: np.ndarray):
        """
        Update the model with a new face encoding (for future enhancement)
        This would be used to add new users to the recognition system
        """
        # This is a placeholder for future implementation
        # Would involve retraining the SVM model with new data
        logger.info(f"📝 New face encoding request for user {user_id} ({name})")
        pass
    
    def cleanup_temp_files(self):
        """
        Clean up temporary files
        """
        try:
            temp_dir = Path("temp")
            if temp_dir.exists():
                for file in temp_dir.glob("*.jpg"):
                    if file.stat().st_mtime < datetime.now().timestamp() - 3600:  # 1 hour old
                        file.unlink()
                        logger.info(f"🗑️ Cleaned up temp file: {file}")
        except Exception as e:
            logger.error(f"❌ Error cleaning temp files: {e}")

# Create global instance
face_recognition_service = FaceRecognitionService()