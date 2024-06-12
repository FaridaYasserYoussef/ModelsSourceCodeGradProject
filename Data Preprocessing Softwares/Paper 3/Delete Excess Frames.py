import csv
import os
import tkinter as tk
from tkinter import filedialog

def delete_image_files(csv_file_path, folder_path):
    try:
        with open(csv_file_path, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row
            
            deleted_files = []
            
            for row in csv_reader:
                if len(row) > 0:  # Ensure row is not empty
                    filename = row[0].strip()  # Get filename from row 1 (index 0)
                    label = row[2].strip() if len(row) > 2 else ''  # Get label from row 3 (index 2)
                    
                    if not label:  # Check if label is empty in row 3
                        image_file_path = os.path.join(folder_path, filename)
                        
                        if os.path.exists(image_file_path) and is_image_file(image_file_path):
                            os.remove(image_file_path)
                            deleted_files.append(filename)
                            print(f"Deleted image file: {filename}")
                        else:
                            print(f"Image file not found or not valid: {filename}")
                    else:
                        print(f"Skipping file with label: {filename}")
            
            if deleted_files:
                print("\nDeleted files:")
                for deleted_file in deleted_files:
                    print(deleted_file)
                print("\nImage deletion process completed.")
            else:
                print("No image files were deleted.")
    
    except Exception as e:
        print(f"Error occurred during image deletion: {str(e)}")

def is_image_file(file_path):
    # Check if the file has a common image extension
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() in image_extensions

def select_folder_and_process_deletion(parent_folder):
    for root, dirs, files in os.walk(parent_folder):
        for file in files:
            if file.lower().endswith('.csv'):
                csv_file_path = os.path.join(root, file)
                delete_image_files(csv_file_path, root)
                break  # Process only the first CSV file found in each subdirectory

def main():
    window = tk.Tk()
    window.title("Image File Deletion Tool")

    instruction_label = tk.Label(window, text="Select a parent folder containing CSV and image files to delete based on conditions.")
    instruction_label.pack(pady=10)

    def select_folder():
        folder_path = filedialog.askdirectory()
        if folder_path:
            select_folder_and_process_deletion(folder_path)

    process_button = tk.Button(window, text="Select Parent Folder and Process Deletion", command=select_folder)
    process_button.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()
