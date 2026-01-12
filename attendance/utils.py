# attendance/utils.py
import os
import json
import numpy as np

try:
    import cv2

    OPENCV_AVAILABLE = True
    print("✅ OpenCV loaded successfully")
except ImportError as e:
    OPENCV_AVAILABLE = False
    print(f"❌ OpenCV not available: {e}")


class FaceRecognition:
    """
    Face recognition utility with fallback to simulation
    """

    @staticmethod
    def recognize_face_from_camera(known_encodings):
        """
        Simulate face recognition for development
        """
        try:
            if not known_encodings:
                return None, "❌ No registered faces found"

            # For simulation, return first employee
            employee_id = list(known_encodings.keys())[0]
            return employee_id, "✅ Face recognized successfully (Simulation Mode)"

        except Exception as e:
            return None, f"❌ Face recognition failed: {str(e)}"

    @staticmethod
    def encode_face_from_image(image_file):
        """
        Encode face from uploaded image with fallback
        """
        try:
            if not image_file:
                return None, "❌ No image provided"

            print(f"DEBUG: Processing image: {image_file.name}")

            if OPENCV_AVAILABLE:
                # Try OpenCV method
                result = FaceRecognition._encode_with_opencv(image_file)
                if result is not None:
                    return result
                else:
                    print("DEBUG: OpenCV method failed, falling back to simulation")

            # Fallback to simulation
            return FaceRecognition._encode_simulation(image_file)

        except Exception as e:
            print(f"DEBUG: Error in encode_face_from_image: {str(e)}")
            return None, f"❌ Face encoding failed: {str(e)}"

    @staticmethod
    def _encode_with_opencv(image_file):
        """
        Try to encode face using OpenCV
        """
        try:
            # Save the uploaded file temporarily
            temp_path = f"/tmp/{image_file.name}"
            with open(temp_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # Load image using OpenCV
            image = cv2.imread(temp_path)

            if image is None:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return None, "❌ Could not read image file"

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Load OpenCV face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            if face_cascade.empty():
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return None, "❌ Could not load face detection model"

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            if len(faces) == 0:
                return None, "❌ No face detected in the image"

            if len(faces) > 1:
                return None, f"❌ Multiple faces detected ({len(faces)} faces found)"

            # Create a simple encoding
            x, y, w, h = faces[0]
            face_region = gray[y:y + h, x:x + w]
            face_encoding = cv2.resize(face_region, (100, 100)).flatten().tolist()

            return face_encoding, "✅ Face encoded successfully with OpenCV"

        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"DEBUG: OpenCV encoding failed: {str(e)}")
            return None

    @staticmethod
    def _encode_simulation(image_file):
        """
        Fallback simulation for face encoding
        """
        try:
            # Create a simulated encoding
            simulated_encoding = [float(hash(image_file.name + str(i)) % 1000) / 1000.0 for i in range(128)]
            return simulated_encoding, "✅ Face encoded successfully (Simulation Mode)"
        except Exception as e:
            return None, f"❌ Simulation encoding failed: {str(e)}"

    @staticmethod
    def verify_single_face(image_file):
        """
        Verify that image contains exactly one face
        """
        try:
            if not image_file:
                return False, "❌ No image provided"

            if OPENCV_AVAILABLE:
                # Try OpenCV verification
                result = FaceRecognition._verify_with_opencv(image_file)
                if result is not None:
                    return result

            # Fallback: assume single face for simulation
            return True, "✅ Single face detected (Simulation)"

        except Exception as e:
            return False, f"❌ Face verification failed: {str(e)}"

    @staticmethod
    def _verify_with_opencv(image_file):
        """
        Verify single face using OpenCV
        """
        try:
            temp_path = f"/tmp/verify_{image_file.name}"
            with open(temp_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            image = cv2.imread(temp_path)

            if image is None:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False, "❌ Could not read image file"

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            if face_cascade.empty():
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False, "❌ Could not load face detection model"

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if os.path.exists(temp_path):
                os.remove(temp_path)

            if len(faces) == 0:
                return False, "❌ No face detected in the image"

            if len(faces) > 1:
                return False, f"❌ Multiple faces detected ({len(faces)} faces found)"

            return True, "✅ Single face detected"

        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"DEBUG: OpenCV verification failed: {str(e)}")
            return None


# Global availability flag
FACE_RECOGNITION_AVAILABLE = True