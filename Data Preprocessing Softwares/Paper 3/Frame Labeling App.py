import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from PIL import Image, ImageTk
from queue import Queue

class FrameLabelingApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Frame Labeling Tool")
        self.geometry("800x950")

        self.folder_paths = Queue()
        self.current_folder_path = None
        self.frame_images = []
        self.timestamps = []
        self.num_frames = 0

        self.start_frame_index = 0
        self.end_frame_index = 0
        self.selected_class = tk.StringVar()

        self.folder_label = tk.Label(self, text="Select Exported Parent Folder:")
        self.folder_label.pack(pady=5)
        
        self.select_button = tk.Button(self, text="Select Parent Folder", command=self.open_parent_folder_selection)
        self.select_button.pack(pady=5)
        
        self.csv_label = tk.Label(self, text="Selected CSV File: ")
        self.csv_label.pack(pady=5)

        self.frame_label = tk.Label(self, width=600, height=400)
        self.frame_label.pack(pady=10)

        self.frame_number_label = tk.Label(self, text="Frame: ")
        self.frame_number_label.pack(pady=5)

        self.end_frame_label = tk.Label(self, width=200, height=133)
        self.end_frame_label.pack(pady=10, padx=20)

        self.class_label = tk.Label(self, text="Select Class Label:")
        self.class_label.pack(pady=5)

        self.class_frame = ttk.Frame(self)
        self.class_frame.pack(pady=5)

        self.class_options = ["Eating", "Mobile_Use", "Drinking", "Phone_Call", "No_Hands", "One_hand", "Smoking", "Two-Hands"]
        for option in self.class_options:
            radio_button = tk.Radiobutton(self.class_frame, text=option, variable=self.selected_class, value=option)
            radio_button.pack(side=tk.LEFT, padx=10)

        self.start_button = tk.Button(self, text="Start", command=self.start_processing, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        self.queue_label = tk.Label(self, text="Queue:")
        self.queue_label.pack(pady=5)

        self.queue_listbox = tk.Listbox(self, width=80, height=15)
        self.queue_listbox.pack(pady=5, side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.frame_slider = tk.Scale(self, from_=0, to=0, orient=tk.HORIZONTAL, length=700, command=self.update_frame)
        self.frame_slider.pack(pady=5, fill=tk.X)

    def open_parent_folder_selection(self):
        parent_folder = filedialog.askdirectory(title="Select Parent Folder")
        if parent_folder:
            self.load_folders_and_subfolders(parent_folder)

    def load_folders_and_subfolders(self, parent_folder):
        for root, dirs, files in os.walk(parent_folder):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                self.folder_paths.put(dir_path)

        if not self.folder_paths.empty():
            self.load_next_folder()

    def load_next_folder(self):
        if not self.folder_paths.empty():
            self.current_folder_path = self.folder_paths.get()
            self.load_frames_and_csv(self.current_folder_path)
            self.enable_start_button()

    def load_frames_and_csv(self, folder_path):
        frame_images = []
        csv_path = os.path.join(folder_path, "video_image_timestamps.csv")
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", f"CSV file not found in folder: {folder_path}")
            return

        df = pd.read_csv(csv_path)
        self.timestamps = df['timestamp'].values
        self.num_frames = len(self.timestamps)

        if self.num_frames > 0:
            self.frame_slider.config(to=self.num_frames - 1)

        for index, row in df.iterrows():
            image_path = os.path.join(folder_path, row['image_path'])
            if os.path.exists(image_path):
                frame_image = Image.open(image_path)
                frame_images.append(frame_image)

        self.frame_images = frame_images

        if self.frame_images:
            self.display_frame(0, self.frame_images[0])
            self.update_end_frame(33)

        self.csv_label.config(text=f"Selected CSV File: {csv_path}")
        self.queue_listbox.insert(tk.END, folder_path)
        self.queue_listbox.selection_clear(0, tk.END)
        self.queue_listbox.selection_set(tk.END)

    def enable_start_button(self):
        if self.current_folder_path and self.frame_images:
            self.start_button.config(state=tk.NORMAL)

    def update_frame(self, event):
        frame_index = int(self.frame_slider.get())
        if 0 <= frame_index < len(self.frame_images):
            frame_image = self.frame_images[frame_index]
            self.display_frame(frame_index, frame_image)
            self.update_end_frame(33)

    def display_frame(self, frame_index, frame_image):
        label_width, label_height = self.frame_label.winfo_width(), self.frame_label.winfo_height()
        resized_image = frame_image.resize((label_width, label_height))

        img = ImageTk.PhotoImage(resized_image)
        self.frame_label.configure(image=img)
        self.frame_label.image = img

        frame_text = f"Frame: {frame_index + 1}"
        self.frame_number_label.config(text=frame_text)

    def update_end_frame(self, offset):
        end_frame_index = int(self.frame_slider.get()) + offset
        if 0 <= end_frame_index < len(self.frame_images):
            end_frame_image = self.frame_images[end_frame_index]
            label_width, label_height = self.end_frame_label.winfo_width(), self.end_frame_label.winfo_height()
            resized_image = end_frame_image.resize((label_width, label_height))

            img = ImageTk.PhotoImage(resized_image)
            self.end_frame_label.configure(image=img)
            self.end_frame_label.image = img

    def start_processing(self):
        if self.current_folder_path and self.frame_images:
            label_value = self.selected_class.get()
            start_frame_index = int(self.frame_slider.get())
            end_frame_index = int(self.frame_slider.get()) + 33

            # Update CSV file with label for specified frame range
            csv_path = os.path.join(self.current_folder_path, "video_image_timestamps.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df.loc[start_frame_index:end_frame_index, 'Label'] = label_value
                df.to_csv(csv_path, index=False)

            # Load and process next folder in the queue
            self.load_next_folder()

if __name__ == "__main__":
    app = FrameLabelingApp()
    app.mainloop()
