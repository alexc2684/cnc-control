import cv2
import time

class Camera:
    """
    Wrapper for OpenCV VideoCapture to simplify image acquisition.
    """
    def __init__(self, source: int = 1):
        """
        Initialize the camera.
        
        Args:
            source (int): The camera source index (default 1).
        """
        self.source = source
        self.cap = cv2.VideoCapture(source)
        
        if not self.cap.isOpened():
            # In a real scenario we might want to raise an error, 
            # but for robustness maybe we just log it?
            # Raising error is better for experiment engine to fail fast.
            raise IOError(f"Cannot open camera source {source}")
            
        # Set resolution to a reasonable default for speed
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Warm up the camera
        for _ in range(10):
            self.cap.read()

    def capture_image(self, filename: str):
        """
        Capture a single frame and save it to the specified filename.
        
        Args:
            filename (str): The path to save the image to.
            
        Raises:
            IOError: If capturing the frame fails.
        """
        if not self.cap.isOpened():
             raise IOError("Camera is not open")
             
        # Retry a few times to get a valid frame
        ret = False
        frame = None
        for _ in range(5):
            ret, frame = self.cap.read()
            if ret:
                break
            time.sleep(0.1)
            
        if not ret:
            raise IOError("Failed to capture frame")
            
        cv2.imwrite(filename, frame)

    def close(self):
        """Release the camera resource."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
