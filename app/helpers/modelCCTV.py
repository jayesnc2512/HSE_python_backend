import cv2
import asyncio
import os
import json
from datetime import datetime
from roboflow import Roboflow
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Optional
import base64
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, sender_password, receiver_email, subject, body):
    # Create the email content
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))

    # Connect to the Gmail SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)  # Login to the server
        text = message.as_string()  # Convert the message to a string
        server.sendmail(sender_email, receiver_email, text)  # Send the email
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()  # Logout from the server


class MongoDBClient:
    def __init__(self, db_url: str, db_name: str):
        try:
            self.client = MongoClient(db_url, serverSelectionTimeoutMS=5000)  # 5 seconds timeout
            self.db = self.client[db_name]
            # Test the connection
            self.client.admin.command('ping')
            print("MongoDB connection established.")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

# Create a single instance of MongoDBClient
mongodb_client = MongoDBClient(
    db_url="mongodb+srv://Jayesh:nfqyqIcoqAMWkjfQ@cluster0.57baeh6.mongodb.net/kongsberg?retryWrites=true&w=majority",
    db_name="kongsberg"  # Replace with your database name
)

# Initialize MongoDB connection
cctv_logs_collection = mongodb_client.get_collection('cctvLogs')

# Initialize Roboflow
api_key = "UxQrTUyiVzo2zC95yPKO"
project_id = "vid_ppe"
version = "1"

# Initialize Roboflow and model
rf = Roboflow(api_key=api_key)
project = rf.workspace().project(project_id)
model = project.version(version).model

def draw_bounding_boxes(image, predictions):
    """Draw bounding boxes and labels on the image."""
    for prediction in predictions:
        x = int(prediction['x'])
        y = int(prediction['y'])
        width = int(prediction['width'])
        height = int(prediction['height'])
        class_name = prediction['class']
        confidence = prediction['confidence']

        # Calculate the top-left and bottom-right points of the bounding box
        top_left = (x - width // 2, y - height // 2)
        bottom_right = (x + width // 2, y + height // 2)

        # Draw the bounding box on the image
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        
        # Construct and put the label above the bounding box
        label = f"{class_name}: {confidence:.2f}"
        cv2.putText(image, label, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def save_annotated_image(image, output_path):
    """Save the annotated image to the specified path."""
    cv2.imwrite(output_path, image)

def analyze_safety_gear(predictions, person_box):
    """Analyze which safety gear is present on a detected person."""
    safety_gear = {
        "Helmet": False,
        "Mask": False,
        "Vest": False,
        "Gloves": False,
        "Shoes": False,
        "Goggles": False,
    }
    
    for detection in predictions:
        if detection['class'] in safety_gear:
            gear_center_x = detection['x']
            gear_center_y = detection['y']

            # Check if gear is inside the person box
            if (person_box['x_min'] <= gear_center_x <= person_box['x_max'] and
                    person_box['y_min'] <= gear_center_y <= person_box['y_max']):
                safety_gear[detection['class']] = True
    
    return safety_gear

def should_log(safety_gear):
    """Check if the person meets the logging criteria."""
    true_attributes = sum(value for value in safety_gear.values())
    return true_attributes <= 5

def encode_frame_as_base64(frame):
    """Encode the frame as a base64 string."""
    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()
    frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
    return frame_base64

async def process_frame(frame, frame_index, output_folder, results_dict, camID):
    # Save the frame temporarily to send to Roboflow
    temp_image_path = os.path.join(output_folder, f"temp_frame_{frame_index}.jpg")
    cv2.imwrite(temp_image_path, frame)
    
    # Perform model inference using Roboflow
    result = model.predict(temp_image_path, confidence=20, overlap=20).json()

    # Extract predictions from the result
    predictions = result["predictions"]

    # Initialize output dictionary
    results = {
        "total_persons": 0,
        "persons": {}
    }

    # Person counter
    person_counter = 1

    # Loop through predictions to find persons and their gear
    for detection in predictions:
        if detection['class'] == 'Person':
            person_box = {
                "x_min": detection['x'] - detection['width'] / 2,
                "x_max": detection['x'] + detection['width'] / 2,
                "y_min": detection['y'] - detection['height'] / 2,
                "y_max": detection['y'] + detection['height'] / 2
            }
            
            # Analyze safety gear for the detected person
            safety_gear = analyze_safety_gear(predictions, person_box)
            
            # Append person info to results, excluding person box coordinates
            results["total_persons"] += 1
            results["persons"][f"Person {person_counter}"] = {
                "safety_gear": safety_gear
            }
            
            # Increment person counter
            person_counter += 1

    # Annotate the image with bounding boxes and labels
    draw_bounding_boxes(frame, predictions)

    # Save the annotated image with the frame index
    output_path = os.path.join(output_folder, f"frame_{frame_index}.jpg")
    save_annotated_image(frame, output_path)

    # Store the results in the dictionary
    results_dict[frame_index] = results

    # Remove the temporary image after processing
    os.remove(temp_image_path)

    # Log data to MongoDB if conditions are met
    timestamp = datetime.utcnow()
    for person, info in results["persons"].items():
        if should_log(info["safety_gear"]):
            frame_base64 = encode_frame_as_base64(frame)
            log_entry = {
                "camID": camID,
                "timestamp": timestamp,
                "person": person,
                "safety_gear": info["safety_gear"],
                "frame": frame_base64
            }
            try:
                cctv_logs_collection.insert_one(log_entry)
                print("Log entry inserted.\n\n\n")
            except PyMongoError as e:
                print(f"Error inserting log entry: {e}")

async def main():
    cap = cv2.VideoCapture("E:/Notes/coding/Kongsberg/python-backend/app/helpers/sample2.mp4")
    frame_index = 0
    output_folder = "./output_frames"
    os.makedirs(output_folder, exist_ok=True)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_interval = fps  # Interval to extract one frame per second
    results_dict = {}
    camID = "Camera_1"  # Assign an appropriate camera ID

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process only one frame per second
        if frame_index % frame_interval == 0:
            await process_frame(frame, frame_index // frame_interval, output_folder, results_dict, camID)

        frame_index += 1
        print(results_dict)
        
        # Wait for 5 seconds before checking logs again
        await asyncio.sleep(5)

    cap.release()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
