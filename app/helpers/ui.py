import tkinter as tk
from tkinter import filedialog, messagebox

class PythonUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Processing")
        self.video_path = tk.StringVar()
        # self.output_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Video path
        tk.Label(self.root, text="Video File Path:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.video_entry = tk.Entry(self.root, textvariable=self.video_path, width=50)
        self.video_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.select_video_path).grid(row=0, column=2, padx=10, pady=10)

        # # Output path
        # tk.Label(self.root, text="Output File Path:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        # self.output_entry = tk.Entry(self.root, textvariable=self.output_path, width=50)
        # self.output_entry.grid(row=1, column=1, padx=10, pady=10)
        # tk.Button(self.root, text="Browse", command=self.select_output_path).grid(row=1, column=2, padx=10, pady=10)

        # Submit button
        tk.Button(self.root, text="Submit", command=self.submit).grid(row=2, column=1, padx=10, pady=20)

    def select_video_path(self):
        video_path = filedialog.askopenfilename(
            title="Select the video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if video_path:
            self.video_path.set(video_path)

    # def select_output_path(self):
    #     output_path = filedialog.asksaveasfilename(
    #         title="Select the output video file",
    #         defaultextension=".avi",
    #         filetypes=[("AVI files", "*.avi")]
    #     )
    #     if output_path:
    #         self.output_path.set(output_path)

    def submit(self):
        video_path = self.video_path.get()
        # output_path = self.output_path.get()
        if video_path :
            # Here you can add the logic to process the video
            print(f"Selected video path: {video_path}")
            self.quit()
        else:
            messagebox.showwarning("Warning", "Please select both video path.")
    
    def quit(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PythonUI(root)
    root.mainloop()
