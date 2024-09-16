import cv2
from inference_sdk import InferenceHTTPClient
import matplotlib.pyplot as plt


class VideoObjectDetection:
    api_url = "https://detect.roboflow.com"
    api_key = "oWW9w4FYndkZO5g4VTUE"  # Replace with your actual API key
    model_id = "ppe-rqnu9/4"
    client = InferenceHTTPClient(api_url=api_url, api_key=api_key)

    @staticmethod
    def resize_frame(frame, max_width=480, max_height=320):
      
        height, width = frame.shape[:2]
        if width > max_width or height > max_height:
            scaling_factor = min(max_width / width, max_height / height)
            frame = cv2.resize(frame, (int(width * scaling_factor), int(height * scaling_factor)))
        return frame

    @staticmethod
    def process_frame(frame):
        # Check if the frame is valid
        if frame is None or frame.size == 0:
            print("Error: Received an empty frame.")
            return None

        try:
            # Resize the frame to prevent dimension errors
            frame = VideoObjectDetection.resize_frame(frame)

            # Perform inference by sending the bytes directly
            result = VideoObjectDetection.client.infer(frame, model_id=VideoObjectDetection.model_id)
            print(result)
            # Process the results and draw bounding boxes
            predictions = result.get("predictions", [])
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

                # Draw the bounding box on the frame
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

                # Construct and put the label above the bounding box
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(frame, label, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            return frame

        except Exception as e:
            print(f"Error processing frame: {e}")
            return None
            
    def detect_from_video(video_path, output_path=None, target_fps=3):
        try:
            print("detect_from_video invoked")
            if video_path=="0" or video_path=="1" or video_path=="2":
                video_path=int(video_path)


            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                    print("Error opening video capture")
                    return

            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            original_fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30  # Default to 30 FPS if not available

            # Calculate the frame interval to achieve target_fps
            frame_interval = int(original_fps / target_fps)
            # frame_interval = int(original_fps / 1) # NO frame skipped


            if output_path:
                out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), target_fps, (frame_width, frame_height))

            frame_number = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Process the frame only if it is the right frame in the sequence
                if frame_number % frame_interval == 0:
                    processed_frame = VideoObjectDetection.process_frame(frame)
                    if processed_frame is not None:
                        # Display using Matplotlib
                        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                        plt.imshow(rgb_frame)
                        plt.axis('off')
                        plt.show(block=False)  # Non-blocking display
                        plt.pause(0.001)  # Adjust pause time as needed
                        if output_path:
                            out.write(processed_frame)

                            
                frame_number += 1

            cap.release()
            if output_path:
                out.release()
            cv2.destroyAllWindows()

        except Exception as err:
            print(f"Error in detect_from_video: {err}")

        def save_frame_as_image(frame, frame_number):
            filename = f"frame_{frame_number:04d}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved frame as {filename}")
