from os import error
from flask import Flask, render_template, request, redirect, url_for , Response , jsonify , json
from pymongo import MongoClient
import ipaddress
import tabulate
import io
from PIL import Image
from datetime import datetime
import os
import cv2
import base64
import uuid
import requests
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt

app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb+srv://mehernimra064:shahzadi123456789@cluster0.mgo1zg0.mongodb.net/")
db = client["object_detection_database"]  
collection_camera = db["camera_add"]  
collection_model = db["Add Model"]
collection_stream=db["View Stream"]
collection_smoke_fall=db['Smoke and fire Detection']
collection_Graphs=db['Graphs']




@app.route("/")
def index():

    camera_id = '1'
    fire_docs = collection_smoke_fall.find({})
    Time_stamp = 'Time_stamp'
    event = 'Event_Occur'


    # Extract timestamps and events from the database
    Time_stamp = [document.get(Time_stamp) for document in collection_smoke_fall.find({})]
    event = [document.get(event) for document in collection_smoke_fall.find({})]


# Calculate the percentage of events for each timestamp
    percentage_events = calculate_percentage_events_fire(Time_stamp, event)


    # Prepare data for the bar chart
    timestamps = list(percentage_events.keys())
    percentage_values = list(percentage_events.values())


    plt.figure(figsize=(5, 4))
    plt.barh(timestamps, percentage_values, color='#4e73df')
    plt.xlabel('Percentage of Events')
    plt.ylabel('Time Stamp')
    plt.title('Percentage of Real time Fire  Detection by Time Stamp')
    plt.grid(False)
    plt.tight_layout()


    # # Save the bar chart as an image
    Graph_save = uuid.uuid4().hex + '.png'
    plt.savefig(f'static/' + Graph_save)

    return render_template("index.html", fire_entities=fire_docs, camera_id=camera_id ,  graphs=Graph_save )


def calculate_percentage_events_fire(timestamps, event):
    # Calculate the total number of events
    total_events = len(event)

    # Count the number of events for each timestamp
    event_counts = {}
    for i in range(0,5):
        timestamp = timestamps[i]
        if timestamp not in event_counts:
            event_counts[timestamp] = 0
        event_counts[timestamp] += 1 if event[i] else 0

    percentage_events = {}
    for timestamp, count in event_counts.items():
        percentage_events[timestamp] = (count / total_events) * 100

    return percentage_events

        
@app.route("/download-image/<image_name>")
def download_images(image_name):
    image_data = collection_smoke_fall.find_one({"image_name": image_name})["frame"]

    if not image_data:
        return jsonify({"error": "Image not found"})

    response = Response(image_data, content_type="image/jpg")
    response.headers["Content-Disposition"] = f"attachment; filename={image_name}.jpg"
    return response





@app.route("/add_camera")
def add_camera():
    return render_template("Add_camera.html")


@app.route("/display_stream")
def display_stream():
    return render_template("display_stream.html")


@app.route("/add_model")
def add_model():
    return render_template("Add_model.html")



@app.route("/view_stream")
def view_stream():

    
    camera_key = 'Camera_ID'
    model_path = 'Model_Name'
    timestamp = 'Time_stamp'



    x = collection_camera.find({})
    y = collection_model.find({})
    fire_data = collection_smoke_fall.find({})




    camera_ids = [document.get(camera_key) for document in x]
    model_paths = [document.get(model_path) for document in y]

    fire_datas = [document.get(timestamp) for document in fire_data]


    return render_template('view_stream.html', camera_ids=camera_ids, model_paths=model_paths,
                           fire_frame_num=fire_datas
                        )


@app.route('/submit_camera', methods=["POST"])
def submit_camera():
    if request.method == "POST":
        data = {
            "Camera_ID": request.form["uniqueId"],
            "Camera_IP": request.form["ipAddress"],
        }
        camera_key = 'Camera_ID'
        camera_ids_exist = [document.get(camera_key) for document in collection_camera.find({})]
        print(camera_ids_exist)
        if data['Camera_ID'] != "" and data['Camera_IP'] != "": 
            if int(data['Camera_ID']) >0:
                if data['Camera_ID'] not in camera_ids_exist:
                     try:
                         ipaddress.ip_address(data['Camera_IP'])
                     except ValueError:
                         return render_template('Add_camera.html', error='Invalid IP address format')

                     collection_camera.insert_one(data)

        else:
            return render_template('Add_camera.html' , error='Camera ID is not Valid Number')
        return render_template('Add_camera.html')


@app.route('/submit_model', methods=["POST"])
def submit_model():
    if request.method == "POST":
        data = {
            "Model_ID": request.form["Model_ID"],
            "Model_Name": request.form["Model_Name"],
            "Model_Path": request.form["Model_Path"],
        }
        model_names='Model_Name'
        model_id='Model_ID'
        model_names = [document.get(model_names) for document in collection_model.find({})]
        model_id = [document.get(model_id) for document in collection_model.find({})]


    
        if data['Model_ID']!="" and data['Model_Name']!="" and data['Model_Path']!="" :
            if int(data['Model_ID']) > 0:
                if data['Model_Name'] not in model_names and data['Model_ID'] not in model_id:
                    collection_model.insert_one(data)
        else: 
            return render_template('Add_model.html')
        return render_template('Add_model.html')
@app.route('/submit_view_stream', methods=["POST"])
def submit_view_stream():
    if request.method == "POST":
        data = {
            "Camera_ID": request.form["camera_id"],
            "Model_path": request.form["model_option"],
            'fire_frame_num' : request.form["smoke_detection_frames"],
        
        }
        camera_id = data['Camera_ID']
        model_name = data['Model_path']
        fire_detection = data['fire_frame_num']


        if fire_detection and model_name == 'smoke and fire detection':
            Time_stamp = 'Time_stamp'
            frame_bytes = collection_smoke_fall.find_one({Time_stamp: fire_detection})["frame"]
            frame_image = Image.open(io.BytesIO(frame_bytes))
            frame_image.save('output_image/fire_output_image/frame.jpg')
            frame_fire = base64.b64encode(frame_bytes).decode('utf-8')

            return render_template('display_stream.html', 
                           model_name=model_name, camera_id=camera_id, 
                           frames_number=fire_detection, frame=frame_fire)


@app.route("/thank_you")
def thank_you():
    return "Thank you for your submission!"


if __name__ == "__main__":
    app.run(debug=True)



