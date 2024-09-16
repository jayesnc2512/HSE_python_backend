import tkinter as tk
from helpers.ui import PythonUI
from helpers.modelCCTV import VideoObjectDetection

def CCTV():
    try:
        # Create a Tkinter root window
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window
        ui = PythonUI(root)# Instantiate the PythonUI class to get paths
        # Run the Tkinter event loop to display the UI
        root.deiconify()  # Show the Tkinter window
        root.mainloop()   # Start the Tkinter event loop
        # Get the paths from the UI
        video_path = ui.video_path.get() 
        output_path = ui.output_path.get()

        if not video_path:
            print("Video path is required.")
            return

        print(f"Video path: {video_path}\nOutput path: {output_path}")

        # Call the VideoObjectDetection method with the selected paths
        VideoObjectDetection.detect_from_video(video_path=video_path, output_path=output_path)

    except Exception as err:
        print("Error in CCTV.py:", err)

if __name__ == "__main__":
    CCTV()
