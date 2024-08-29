import asyncio
from inference_sdk import InferenceHTTPClient

class modelAPI:
    async def model(img):
        CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key="oWW9w4FYndkZO5g4VTUE"
        )
        # Use await to call async method
        result = await CLIENT.infer_async(img, model_id="ppe-rqnu9/4")
        return result
    

    async def kioskInference(img):
        modelResult = await modelAPI.model(img)

        # Initialize dictionary to store detection results
        safety_gear = {
            "Helmet": False,
            "Mask": False,
            "Vest": False,
            "Gloves": False,
            "Shoes": False,
            "Goggles":False,
        }

        person_box = None
        
        # Parse results to find the person bounding box
        for detection in modelResult['predictions']:
            if detection['class'] == 'Person':
                # Extract the bounding box for the detected person
                person_box = {
                    "x_min": detection['x'] - detection['width'] / 2,
                    "x_max": detection['x'] + detection['width'] / 2,
                    "y_min": detection['y'] - detection['height'] / 2,
                    "y_max": detection['y'] + detection['height'] / 2
                }
                break  # Assuming only one person, exit loop after finding the first

        if not person_box:
            # If no person is detected, return result with all False
            return safety_gear

        # Check for each safety gear within the person's bounding box
        for detection in modelResult['predictions']:
            if detection['class'] in safety_gear:
                gear_center_x = detection['x']
                gear_center_y = detection['y']

                # Check if gear is inside the person box
                if (person_box['x_min'] <= gear_center_x <= person_box['x_max'] and
                        person_box['y_min'] <= gear_center_y <= person_box['y_max']):
                    safety_gear[detection['class']] = True

        return safety_gear


    
