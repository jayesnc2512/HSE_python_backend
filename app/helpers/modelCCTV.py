import cv2
from inference_sdk import InferenceHTTPClient

class VideoObjectDetection:
    api_url = "https://detect.roboflow.com"
    api_key = "oWW9w4FYndkZO5g4VTUE"  # Replace with your actual API key
    model_id = "ppe-rqnu9/4"
    client = InferenceHTTPClient(api_url=api_url, api_key=api_key)

    @staticmethod
    def resize_frame(frame, max_width=480, max_height=320):
        """
        Resize the frame to a manageable size if it exceeds max dimensions.
        """
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

            # Encode the frame to JPEG format in memory
            success, encoded_image = cv2.imencode('.jpg', frame)
            if not success:
                print("Error encoding frame")
                return frame

            # Perform inference by sending the bytes directly
            result = VideoObjectDetection.client.infer(encoded_image, model_id=VideoObjectDetection.model_id)

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

    @staticmethod
    def detect_from_video(video_path, output_path=None):
        try:
            # Capture video from file or webcam
            cap = cv2.VideoCapture(video_path)

            # Get video dimensions and frame rate
            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            # Video writer to save the output if output_path is provided
            if output_path:
                out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Process the current frame and draw detections
                processed_frame = VideoObjectDetection.process_frame(frame)

                # Display the frame with bounding boxes
                if processed_frame is not None:
                    cv2.imshow("Detected Video", processed_frame)

                # Save frame to output video if required
                if output_path and processed_frame is not None:
                    out.write(processed_frame)

                # Break the loop when 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Release video capture and writer objects
            cap.release()
            if output_path:
                out.release()

            # Close OpenCV windows
            cv2.destroyAllWindows()
        except Exception as err:
            print(f"Error in detect_from_video: {err}")
