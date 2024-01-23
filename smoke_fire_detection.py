import cv2
import numpy as np
from ultralytics import YOLO
import pymongo
import os
from PIL import Image
from datetime import datetime
import base64
import io


# Connect to the MongoDB database.
client = pymongo.MongoClient("mongodb+srv://mehernimra064:shahzadi123456789@cluster0.mgo1zg0.mongodb.net/")
db = client["object_detection_database"]
collection = db["Smoke and fire Detection"]

# Load the YOLOv8 model.
model = YOLO('Models/best.pt')

# Create a variable to store the frame number.
frame_number = 1

# Open the video file.
cap = cv2.VideoCapture("input_video/fire1.mp4")

x_line = 600


while True:
    # Read a frame from the video
    success, frame = cap.read()
    width = int(cap.get(3))
    height = int(cap.get(4))
    if success:
        # Run YOLOv8 inference on the frame
        resized_frame = cv2.resize(frame, (480, 480), interpolation=cv2.INTER_LINEAR)
        results = model(resized_frame)

        current_date_time = datetime.now()
        dt_string = current_date_time.strftime("%d/%m/%Y %H:%M:%S")

        if len(results[0]) > 0:
            image_bytes = io.BytesIO()
            Image.fromarray(resized_frame).save(image_bytes, format='JPEG')
            frame_data_document = {
                'frame_number': frame_number,
                'Event_Occur'  : 'Fire Detection' ,
                'Time_stamp' : dt_string ,
                'frame': image_bytes.getvalue(),
                'image_name' : 'frame' + str(frame_number) + ".png" 
                
                }
            im = Image.open(image_bytes)

            try:
                collection.insert_one(frame_data_document)
            except pymongo.errors.DuplicateKeyError as e:
                # Handle duplicate key error (if needed)
                print(f"Duplicate key error: {e}")

            # Increment the frame number
            frame_number += 1

        # Display the annotated frame
        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 Inference", annotated_frame)

        # If the 'q' key is pressed, quit the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()