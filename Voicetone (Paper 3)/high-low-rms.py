import librosa
import numpy as np
import os

def detect_speaking_intensity(audio_file, threshold):
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)
    
    # Calculate the RMS amplitude of the audio signal
    rms_values = librosa.feature.rms(y=y)  # Compute RMS amplitude frame-by-frame  |  #frame_length=2048, hop_length=512
    # Root Mean Sqaure

    # Find the maximum RMS value (loudest point)
    max_rms = np.max(rms_values)  # Find the maximum RMS value
    
    # Determine if the speaking intensity is loud or calm based on the threshold
    if max_rms >= threshold:
        return "Loud", max_rms
    else:
        return "Calm", max_rms

# Define thresholds for male and female voices
male_threshold = 0.075 
female_threshold = 0.075

# Iterate through folders for male and female voices
folders = [("male voices/Loud", male_threshold),   
           ("male voices/Low", male_threshold), 
           ("female voices/Loud", female_threshold), 
           ("female voices/Low", female_threshold)]

# Iterate through folders and classify speaking intensity
for folder, threshold in folders:
    print("Folder:", folder)
    for file_name in os.listdir(folder):
        if file_name.endswith(".wav"):
            audio_file_path = os.path.join(folder, file_name)
            intensity, energy = detect_speaking_intensity(audio_file_path, threshold)
            print(f"Speaking intensity of {file_name} is: {intensity}, Energy: {energy:.4f}")
