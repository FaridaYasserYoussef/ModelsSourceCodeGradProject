import os
import cv2
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class VideoFrameExtractorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Video Frame Extractor")
        self.geometry("500x350")

        # Create a label for instructions
        self.label = tk.Label(self, text="Select a folder containing video files:", pady=20)
        self.label.pack()

        # Create a button to select folder
        self.select_button = tk.Button(self, text="Select Folder", command=self.select_folder)
        self.select_button.pack(pady=10)

        # Initialize progress variables
        self.progress_var = tk.DoubleVar()
        self.progress_label = tk.Label(self, text="", pady=10)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, length=400, mode='determinate')

        # Create buttons for batch processing
        self.start_button = tk.Button(self, text="Start Batch Processing", command=self.start_processing)
        self.reset_button = tk.Button(self, text="Reset Selection", command=self.reset_selection)
        self.stop_button = tk.Button(self, text="Stop Processing", command=self.stop_processing, state=tk.DISABLED)

        # List to store selected video files
        self.video_files = []
        self.processing = False
        self.process_thread = None

    def select_folder(self):
        # Prompt user to select a folder
        folder_path = filedialog.askdirectory(title="Select Folder")

        if folder_path:
            self.collect_video_files(folder_path)
            if self.video_files:
                message = f"Selected {len(self.video_files)} video files"
                self.progress_label.config(text=message)
            else:
                self.progress_label.config(text="No video files found in the selected folder.")

    def collect_video_files(self, folder_path):
        # Recursively collect all video files (e.g., .mp4 files) within the folder and its subfolders
        self.video_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    self.video_files.append(os.path.join(root, file))

    def start_processing(self):
        if self.processing:
            messagebox.showinfo("Processing in Progress", "Batch processing is already in progress.")
            return

        if not self.video_files:
            messagebox.showwarning("No Video Files", "No video files selected. Please select a folder containing video files.")
            return

        # Start batch processing in a separate thread
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.process_thread = threading.Thread(target=self.batch_processing_thread)
        self.process_thread.start()

    def stop_processing(self):
        if self.process_thread and self.process_thread.is_alive():
            self.processing = False
            self.stop_button.config(state=tk.DISABLED)

    def batch_processing_thread(self):
        total_files = len(self.video_files)
        for index, video_file in enumerate(self.video_files, start=1):
            if not self.processing:
                break
            self.process_video(video_file)
            # Update progress information
            progress_message = f"Processing file {index} of {total_files}"
            self.progress_label.config(text=progress_message)
            # Update progress bar
            progress_value = (index / total_files) * 100
            self.progress_var.set(progress_value)
            self.update_idletasks()  # Refresh GUI to update progress bar and label

        # Reset GUI after processing completes or stops
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("Processing Complete", "Batch processing completed.")

    def process_video(self, video_file):
        # Extract folder path and file name
        folder_path, file_name = os.path.split(video_file)

        # Create output folder for frames and CSV
        output_folder = os.path.join(folder_path, f"{os.path.splitext(file_name)[0]}_frames")
        os.makedirs(output_folder, exist_ok=True)

        # Open video file
        cap = cv2.VideoCapture(video_file)
        frame_count = 0
        data = []

        # Read frames and extract timestamps
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Save frame as image
            frame_filename = os.path.join(output_folder, f'frame_{frame_count:04d}.jpg')
            cv2.imwrite(frame_filename, frame)

            # Get timestamp of current frame
            timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)

            # Append data to list
            data.append({'image_path': os.path.basename(frame_filename), 'timestamp': timestamp_ms, 'Label': ''})

            frame_count += 1

        # Release video capture
        cap.release()

        # Create DataFrame
        df_video_data = pd.DataFrame(data, columns=['image_path', 'timestamp', 'Label'])

        # Save DataFrame to CSV
        csv_output_path = os.path.join(output_folder, 'video_image_timestamps.csv')
        df_video_data.to_csv(csv_output_path, index=False)

    def reset_selection(self):
        self.video_files = []
        self.progress_label.config(text="")
        self.progress_var.set(0)
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = VideoFrameExtractorApp()

    # Place widgets in the window
    app.progress_label.pack()
    app.progress_bar.pack(pady=20)
    app.start_button.pack(pady=10)
    app.reset_button.pack(pady=10)
    app.stop_button.pack(pady=10)

    app.mainloop()
