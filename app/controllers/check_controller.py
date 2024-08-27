# app/controllers/auth_controller.py
from app.DB.mongodb import mongodb_client
from pymongo.collection import Collection
from typing import Dict, Optional
from bson import ObjectId
from pymongo.errors import PyMongoError
from ..helpers.model.checkImage import detect_safety_gear
import base64





class checkController:
    def checkImages(empId, images):
        try:
            saved_images = []
            for idx, image_base64 in enumerate(images):
                # Decode the base64 image (synchronously)
                image_data = base64.b64decode(image_base64.split(",")[1])

                image_path = f"./app/helpers/model/images/{empId}_image_{idx + 1}.png"  
                
                # Save the decoded image data to a file (synchronously)
                with open(image_path, "wb") as image_file:
                    image_file.write(image_data)
                    saved_images.append(image_path)

            print("Saved images:", saved_images)
            
            # Call the synchronous function without awaiting
            detection_results = detect_safety_gear()

            return detection_results

        except Exception as e:
            print(f"Error saving images: {e}")
            return None
