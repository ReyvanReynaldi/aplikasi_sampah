from flask import Flask, render_template, Response, jsonify
import cv2
from ultralytics import YOLO
import os
import threading
import base64
import numpy as np
from flask_socketio import SocketIO, emit
import logging
from pathlib import Path
from flask_cors import CORS
import eventlet


# Patch eventlet
eventlet.monkey_patch()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Constants
MODEL_PATH = Path(__file__).parent / 'weights' / 'best.pt'
DETECTION_THRESHOLD = 0.45
FRAME_RATE_DELAY = 0.02

class Camera:
    def __init__(self):
        self.video = None
        self.initialize_camera()

    def initialize_camera(self):
        try:
            self.video = cv2.VideoCapture(0)
            # set resolusi biar gacor gambarnya
            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            if not self.video.isOpened():
                raise RuntimeError("Could not open camera")
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            raise

    def __del__(self):
        if self.video and self.video.isOpened():
            self.video.release()

    def get_frame(self):
        if not self.video or not self.video.isOpened():
            return None
        
        success, frame = self.video.read()
        if success:
            # flip frame biar ga mirror
            return frame
        return None

class ObjectDetector:
    def __init__(self):
        try:
            # Meningkatkan konfidence model
            self.model = YOLO(str(MODEL_PATH))
            self.model.conf = 0.45  # Set confidence threshold
            self.is_detecting = False
            self.camera = None
            self.detection_thread = None
            # ngasih warna buat masing" jenis sampah
            self.colors = {
                'organik': (0, 255, 0),     # Hijau
                'anorganik': (0, 0, 255),   # Merah
                'b3': (255, 0, 0)           # Biru
            }
        except Exception as e:
            logger.error(f"Model initialization error: {e}")
            raise

    def process_detections(self, frame):
        # buat copyan frame buat deteksi
        detection_frame = frame.copy()
        
        # ngelakuin deteksi
        results = self.model(detection_frame)
        detected_objects = []

        # ngeproses hasil deteksi
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0].tolist())
            conf = float(result.conf[0].item())
            cls = int(result.cls[0].item())
            
            if conf > DETECTION_THRESHOLD:
                label = self.model.names[cls]
                color = self.colors.get(label.lower(), (255, 255, 255))
                
                # ngasih informasi detail untuk frontend
                detected_objects.append({
                    'label': label,
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2],
                    'description': self.get_waste_description(label)
                })
                
                # buat gambar box deteksi
                cv2.rectangle(detection_frame, (x1, y1), (x2, y2), color, 2)
                
                # ngasih label dengan background
                label_text = f'{label} {conf:.2f}'
                text_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                cv2.rectangle(detection_frame, (x1, y1 - text_size[1] - 10), 
                            (x1 + text_size[0], y1), color, -1)
                cv2.putText(detection_frame, label_text, 
                           (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (255, 255, 255), 2)

        return detection_frame, detected_objects

    def get_waste_description(self, label):
        descriptions = {
            'organik': {
                'title': 'Sampah Organik',
                'description': 'Sampah yang dapat terurai secara alami seperti sisa makanan, daun, dan bangkai.',
                'handling': 'Dapat diolah menjadi kompos atau pupuk organik.',
                'examples': 'Contoh: sisa nasi, sayuran, kulit buah, daun kering.',
                'decomposition_time': 'Waktu penguraian: 2-4 minggu'
            },
            'anorganik': {
                'title': 'Sampah Anorganik',
                'description': 'Sampah yang sulit terurai secara alami seperti plastik, kaca, dan logam.',
                'handling': 'Sebaiknya didaur ulang atau diolah kembali.',
                'examples': 'Contoh: botol plastik, kaleng, kertas, kardus.',
                'decomposition_time': 'Waktu penguraian: 50-100 tahun atau lebih'
            },
            'b3': {
                'title': 'Sampah B3 (Bahan Berbahaya dan Beracun)',
                'description': 'Sampah yang mengandung zat berbahaya dan beracun.',
                'handling': 'Harus ditangani khusus dan tidak boleh dicampur dengan sampah lain.',
                'examples': 'Contoh: baterai, lampu neon, pestisida, limbah medis.',
                'warning': 'PERHATIAN: Sampah ini berbahaya bagi kesehatan dan lingkungan!'
            }
        }
        return descriptions.get(label.lower(), {
            'title': 'Tidak Teridentifikasi',
            'description': 'Jenis sampah tidak dapat diidentifikasi dengan jelas.',
            'handling': 'Silakan periksa kembali atau konsultasikan dengan pengelola sampah.'
        })

    def detect_objects(self):
        while self.is_detecting and self.camera:
            try:
                frame = self.camera.get_frame()
                if frame is None:
                    continue

                # Proses deteksi
                frame_with_detection, detected_objects = self.process_detections(frame)
                
                # Encode frame buat streaming/realtime
                _, buffer = cv2.imencode('.jpg', frame_with_detection, 
                                       [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # ngirim hasil ke frontend
                socketio.emit('detection_result', {
                    'frame': frame_base64,
                    'detections': detected_objects
                })
                
                socketio.sleep(FRAME_RATE_DELAY)
            
            except Exception as e:
                logger.error(f"Detection error: {e}")
                self.stop_detection()
                socketio.emit('detection_error', {'error': str(e)})

    def start_detection(self):
        try:
            self.camera = Camera()
            self.is_detecting = True
            self.detection_thread = threading.Thread(target=self.detect_objects)
            self.detection_thread.start()
            return True
        except Exception as e:
            logger.error(f"Start detection error: {e}")
            return False

    def stop_detection(self):
        self.is_detecting = False
        if self.detection_thread:
            self.detection_thread.join()
        if self.camera:
            self.camera.__del__()
            self.camera = None

detector = ObjectDetector()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')
    detector.stop_detection()

@socketio.on('start_detection')
def handle_start_detection():
    if detector.start_detection():
        emit('detection_started', {'status': 'success'})
    else:
        emit('detection_error', {'error': 'Failed to start detection'})

@socketio.on('stop_detection')
def handle_stop_detection():
    detector.stop_detection()
    emit('detection_stopped')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, 
                debug=False,  # Set False for production
                host='0.0.0.0',
                port=port,
                log_output=True)