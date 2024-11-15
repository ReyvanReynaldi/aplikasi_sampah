from ultralytics import YOLO

# Melatih model
model = YOLO('yolov8n.pt')  # Menggunakan model pretrained
model.train(data='/Users/reyvanreynaldi/uas_pc/apk_sampah/dataset_sampah/data.yaml', epochs=50, imgsz=640)  # Ganti dengan path ke data.yaml