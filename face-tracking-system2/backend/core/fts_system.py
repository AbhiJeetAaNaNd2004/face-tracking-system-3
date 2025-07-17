"""
Face Tracking System - Core Implementation
==========================================
This module provides the core face tracking functionality including face detection,
recognition, and video streaming capabilities using InsightFace and OpenCV.
"""

import cv2
import numpy as np
import logging
import time
from typing import List, Dict, Optional, Tuple, Generator
from insightface.app import FaceAnalysis
from db.db_manager import DatabaseManager
from app.config import settings
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class FaceTrackingSystem:
    """
    Core face tracking system for detection and recognition.
    """
    
    def __init__(self, face_app: FaceAnalysis):
        self.face_app = face_app
        self.db_manager = DatabaseManager()
        self.known_embeddings = []
        self.known_labels = []
        self.embedding_lock = threading.RLock()
        self.last_reload_time = 0
        self.reload_interval = 300  # 5 minutes
        
        # Load initial embeddings
        self.reload_embeddings_and_rebuild_index()
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces in a frame and return face information.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of face detection results
        """
        try:
            faces = self.face_app.get(frame)
            results = []
            
            for face in faces:
                # Get face embedding
                embedding = face.embedding
                
                # Find best match
                employee_id, confidence = self._find_best_match(embedding)
                
                # Get bounding box
                bbox = face.bbox.astype(int)
                
                face_info = {
                    'employee_id': employee_id,
                    'confidence': confidence,
                    'bbox': bbox.tolist(),
                    'embedding': embedding,
                    'landmarks': face.kps.tolist() if hasattr(face, 'kps') else None
                }
                
                results.append(face_info)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []
    
    def _find_best_match(self, embedding: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Find the best matching employee for a face embedding.
        
        Args:
            embedding: Face embedding to match
            
        Returns:
            Tuple of (employee_id, confidence_score)
        """
        with self.embedding_lock:
            if not self.known_embeddings:
                return None, 0.0
            
            try:
                # Calculate similarities
                similarities = []
                for known_embedding in self.known_embeddings:
                    similarity = np.dot(embedding, known_embedding) / (
                        np.linalg.norm(embedding) * np.linalg.norm(known_embedding)
                    )
                    similarities.append(similarity)
                
                # Find best match
                best_idx = np.argmax(similarities)
                best_similarity = similarities[best_idx]
                
                # Check if similarity meets threshold
                if best_similarity >= settings.FACE_RECOGNITION_TOLERANCE:
                    return self.known_labels[best_idx], best_similarity
                else:
                    return None, best_similarity
                    
            except Exception as e:
                logger.error(f"Error in face matching: {e}")
                return None, 0.0
    
    def reload_embeddings_and_rebuild_index(self):
        """
        Reload embeddings from database and rebuild the recognition index.
        """
        try:
            current_time = time.time()
            if current_time - self.last_reload_time < self.reload_interval:
                return
            
            with self.embedding_lock:
                embeddings, labels = self.db_manager.get_all_active_embeddings()
                self.known_embeddings = embeddings
                self.known_labels = labels
                self.last_reload_time = current_time
                
                logger.info(f"Reloaded {len(embeddings)} embeddings for {len(set(labels))} employees")
                
        except Exception as e:
            logger.error(f"Error reloading embeddings: {e}")


class FaceTrackingPipeline:
    """
    Main pipeline for face tracking operations.
    """
    
    def __init__(self):
        try:
            # Initialize InsightFace
            self.face_app = FaceAnalysis(
                name='antelopev2',
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
            )
            self.face_app.prepare(ctx_id=0, det_size=(416, 416))
            
            # Initialize tracking system
            self.system = FaceTrackingSystem(self.face_app)
            
            logger.info("Face tracking pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize face tracking pipeline: {e}")
            raise


def generate_mjpeg(camera_id: int, cap: cv2.VideoCapture) -> Generator[bytes, None, None]:
    """
    Generate MJPEG stream with face detection overlay.
    
    Args:
        camera_id: Camera identifier
        cap: OpenCV VideoCapture object
        
    Yields:
        MJPEG frame bytes
    """
    pipeline = FaceTrackingPipeline()
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Failed to read frame from camera {camera_id}")
                break
            
            frame_count += 1
            
            # Process every 5th frame for face detection to reduce CPU load
            if frame_count % 5 == 0:
                try:
                    faces = pipeline.system.detect_faces(frame)
                    
                    # Draw face detection results
                    for face in faces:
                        bbox = face['bbox']
                        employee_id = face['employee_id']
                        confidence = face['confidence']
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                        
                        # Draw label
                        if employee_id:
                            label = f"{employee_id} ({confidence:.2f})"
                            cv2.putText(frame, label, (bbox[0], bbox[1] - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        else:
                            cv2.putText(frame, "Unknown", (bbox[0], bbox[1] - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                except Exception as e:
                    logger.error(f"Error processing frame: {e}")
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue
            
            # Yield MJPEG frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
    except Exception as e:
        logger.error(f"Error in MJPEG generation: {e}")
    finally:
        logger.info(f"MJPEG stream ended for camera {camera_id}")