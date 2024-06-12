import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
import os
import pandas as pd
from datetime import datetime, timedelta
import threading

class Kalman:
    Q = 0.00001
    R = 0.001
    P = 1
    X = 0
    K = 0

    def __init__(self, initValue, initR):
        self.X = initValue
        self.R = initR

    def setInit(self, newInit):
        X = newInit

    def measurementUpdate(self):
        self.K = (self.P + self.Q) / (self.P + self.Q + self.R)
        self.P = self.R * (self.P + self.Q) / (self.P + self.Q + self.R)

    def update(self, measurement):
        self.measurementUpdate()
        self.X = self.X + (measurement - self.X) * self.K
        return self.X

original_file_path = None  # Variable to store the original file path

def on_drop(event):
    file_path = root.tk.splitlist(event.data)
    if file_path and is_csv(file_path[0]):
        show_file_info(file_path[0])

def browse_file():
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
    for file_path in file_paths:
        # Set the original_file_path for the browse button
        original_file_path = file_path
        show_file_info(file_path)

# More GUI Stuff
def show_file_info(file_path):
    global original_file_path, dropped_files  # Use the global variables
    dropped_files.append(file_path)
    original_file_path = dropped_files[0]  # Set original_file_path to the first file in the list
    file_name = os.path.basename(file_path)
    file_directory = os.path.dirname(file_path)
    #feedback_label.config(text=f"File Name: {file_name}\nDirectory: {file_directory}")

    # Add the file name to the listbox
    files_listbox.insert(tk.END, file_name)
    # Select the last item in the list to show the most recently added file
    files_listbox.select_set(tk.END)

def clear_file_list():
    files_listbox.delete(0, tk.END)

# Variable to store the list of dropped file paths
dropped_files = []

def on_drop(event):
    file_paths = root.tk.splitlist(event.data)
    for file_path in file_paths:
        if file_path and is_csv(file_path):
            dropped_files.append(file_path)
            show_file_info(file_path)

def preprocess_in_thread():
    # Disable the preprocess button
    preprocess_button.config(state=tk.DISABLED)
    # Create a new thread for preprocessing
    preprocess_thread = threading.Thread(target=preprocess, daemon=True)
    preprocess_thread.start()
    # Periodically check the thread status and re-enable the button when preprocessing is complete
    root.after(100, check_thread_status, preprocess_thread)

def check_thread_status(thread):
    if thread.is_alive():
        # If the thread is still running, schedule another check
        root.after(100, check_thread_status, thread)
    else:
        # If the thread is complete, re-enable the preprocess button
        preprocess_button.config(state=tk.NORMAL)

def preprocess():
    global dropped_files  # Use the global variable
    for file_path in dropped_files:
        if is_csv(file_path):
            # try:
            preprocessed_file_path = preprocess_csv(file_path)
            print("Preprocessed File Path:", preprocessed_file_path)
            show_success_message(os.path.basename(file_path))
            # except:
            #     show_fail_message(os.path.basename(file_path))
    # Reset the list of dropped files after processing
    dropped_files = []
    # Clear the list of imported files from the GUI
    clear_file_list()
    # Enable the preprocess button after processing is completed
    preprocess_button.config(state=tk.NORMAL)

################# GUI Control Buttons #################

def print_toggle_convert_time():
    global Toggle_Convert_Time_Num  
    print(Toggle_Convert_Time_Num.get())
    
def select_interpolation_method():
    global interpolation_method_var
    print(interpolation_method_var.get())

def validate_numeric_input(new_value):
    try:
        float(new_value)
        return True
    except ValueError:
        return False

########################################################

# All CSV Operation are here
def preprocess_csv(original_file_path):
    df = pd.read_csv(original_file_path)

    #------ Try to apply Kalman Filter ------#
    try:
        # Kalman filter initialization
        filteredAccX = Kalman(0, 0.0001)
        filteredAccY = Kalman(0, 0.0001)
        filteredAccZ = Kalman(0, 0.0001)

        # Apply Kalman filtering to columns 'ax', 'ay', 'az'
        df['kacc_x'] = df['ax'].apply(filteredAccX.update)
        df['kacc_y'] = df['ay'].apply(filteredAccY.update)
        df['kacc_z'] = df['az'].apply(filteredAccZ.update)
    except:
        print("No ax,ay,az to Apply Kalman Filter")

    #-- Add clock time in case there's no column --#
    global Toggle_Convert_Time_Num  
    if Toggle_Convert_Time_Num.get() == 1:
        # Extract the time from the "time" column in the first row
        time_value = df.loc[0, 'time']

        # Initialize a base time for the entire DataFrame
        base_time = datetime.strptime('10:00:00.000', '%H:%M:%S.%f')

        try:
            # Try to parse the time value as a valid time format
            pd.to_datetime(time_value, format='%H:%M:%S:%f')
            print("Correct Time Format Detected")
        except ValueError:
            # Print False if the time value is not in the expected format
            print("Wrong Time Format")

            # Convert Time Format
            for index, row in df.iterrows():
                # Convert elapsed time to 'hh:mm:ss:mmm' format starting from base_time
                elapsed_value = row['time']

                # Convert elapsed time to timedelta
                elapsed_timedelta = timedelta(seconds=elapsed_value)

                # Calculate the elapsed time for each row independently
                final_time = base_time + elapsed_timedelta

                # Update the 'time' column with the formatted string
                df.at[index, 'time'] = final_time.strftime('%H:%M:%S:%f')#[:-3]
    
    #-- Try Rename specified columns to match other data set--#
    try:
        df.rename(columns={'ax': 'acc_x', 'ay': 'acc_y', 'az': 'acc_z', 'wx': 'gyro_x', 'wy': 'gyro_y', 'wz': 'gyro_z'}, inplace=True)
    except:
        print("Nothing Rename")

    # Drop any unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # For Resampling
    df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S:%f')

    # Set 'time' column as the index
    df.set_index('time', inplace=True)

    # Convert all numeric columns to numeric format (excluding 'time' column)
    df[df.columns.difference(['time'])] = df[df.columns.difference(['time'])].apply(pd.to_numeric, errors='coerce')

    #--- Fix the time index that are duplicated by adding correct milliseconds ---#
    # df['milliseconds'] = df.groupby('time').cumcount()
    # df['milliseconds'] = df['milliseconds'] * (1000000 / len(df['milliseconds'].unique()))
    # df['time'] = df['time'] + pd.to_timedelta(df['milliseconds'], unit='us')
   
    # Interapolate / Extrapolate
    global interpolation_method_var
    global Numeric_Input_Value

    print(Numeric_Input_Value.get())
    
    if interpolation_method_var.get() == "Interpolation":
        
        # Remove duplicate time
        df_resampled = df[~df.index.duplicated(keep='first')]
               
        # Make sure that inerpolation is done correctly
        pass
        # resampling_frequency = str(Numeric_Input_Value.get()) + 'ms'
        # df_resampled = df.resample(resampling_frequency).interpolate(method='linear')


    if interpolation_method_var.get() == "Extrapolation":
        pass
        # df_resampled = df.resample(str(Numeric_Input_Value.get())+'ms').interpolate(method='linear', limit_area='outside')

    # Reset the index to include 'time' column in the result
    df_resampled.reset_index(inplace=True)

    # Extract only the time component from the datetime index
    df_resampled['time'] = df_resampled['time'].dt.strftime('%H:%M:%S:%f')
    #-------------------#
    
    # Save the preprocessed data to a new file
    preprocessed_file_name = os.path.basename(original_file_path).replace('.csv', '-preprocessed.csv')
    preprocessed_file_path = os.path.join(os.path.dirname(original_file_path), preprocessed_file_name)
    df_resampled.to_csv(preprocessed_file_path, index=False)
    
    return preprocessed_file_path

def is_csv(file_path):
    return file_path.lower().endswith(".csv")

def show_success_message(file_name):
    success_message = f"{file_name} Preprocessed successfully!\n"
    success_text.insert(tk.END, success_message)
    success_text.see(tk.END)  # Scroll to the bottom of the text field

def show_fail_message(file_name):
    fail_message = f"{file_name} FAILED! Error Occured!\n"
    success_text.insert(tk.END, fail_message)
    success_text.see(tk.END)  # Scroll to the bottom of the text field

root = TkinterDnD.Tk()

root.title("Data Preprocessing v0.2")
root.attributes('-alpha', 0.8)
root.geometry("600x550")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(pady=50)

# Make the text bold
feedback_label = tk.Label(frame, text="Drag and drop CSV files here\nor click browse", font=("Helvetica", 12, "bold"))
feedback_label.pack()

frame.drop_target_register(DND_FILES)
frame.dnd_bind('<<Drop>>', on_drop)

browse_button = tk.Button(frame, text="Browse", command=browse_file)
browse_button.pack()

preprocess_button = tk.Button(frame, text="Preprocess", command=preprocess_in_thread)
preprocess_button.pack()

########################################################

# Convert Time Checkbox
Toggle_Convert_Time_Num = tk.IntVar()  # Global variable to store the state of the checkbox
convert_time_checkbox = tk.Checkbutton(frame, text="Convert Time to hh:mm:ss", variable=Toggle_Convert_Time_Num, onvalue=1, offvalue=0, command=print_toggle_convert_time)
convert_time_checkbox.pack()

# Radio Button
interpolation_method_var = tk.StringVar(value="Interpolation")  # Default value is "Interpolation", Global variable to store radio button
interpolation_radio_interpolation = tk.Radiobutton(frame, text="Interpolation", variable=interpolation_method_var, value="Interpolation", command=select_interpolation_method)
interpolation_radio_interpolation.pack()
interpolation_radio_extrapolation = tk.Radiobutton(frame, text="Extrapolation", variable=interpolation_method_var, value="Extrapolation", command=select_interpolation_method)
interpolation_radio_extrapolation.pack()

# Add numeric input field
Numeric_Input_Value = tk.StringVar() # Global variable to store ms
numeric_input_label = tk.Label(frame, text="Data Point every x Millisecond(s)")
numeric_input_label.pack()
numeric_input_entry = tk.Entry(frame, textvariable=Numeric_Input_Value, validate="key", validatecommand=(root.register(validate_numeric_input), "%P"))
numeric_input_entry.pack()

########################################################

# Text widget to display success messages with scrollbar
success_text = tk.Text(frame, height=10, width=40, font=("Helvetica", 10), wrap=tk.WORD)
success_text.pack(side=tk.LEFT, fill=tk.Y)

scrollbar = tk.Scrollbar(frame, command=success_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
success_text.config(yscrollcommand=scrollbar.set)

# Updates to List - Listbox to display imported files
files_listbox = tk.Listbox(frame, height=10, width=40, font=("Helvetica", 10), selectmode=tk.MULTIPLE)
files_listbox.pack(side=tk.LEFT, fill=tk.Y)

scrollbar_listbox = tk.Scrollbar(frame, command=files_listbox.yview)
scrollbar_listbox.pack(side=tk.RIGHT, fill=tk.Y)
files_listbox.config(yscrollcommand=scrollbar_listbox.set)

root.mainloop()

