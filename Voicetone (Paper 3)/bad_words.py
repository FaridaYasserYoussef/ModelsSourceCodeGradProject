import os
import csv
import speech_recognition as sr

def transcribe_audio(file_path):
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)  # Read the entire audio file
            text = recognizer.recognize_google(audio_data)  # Use Google Speech Recognition to convert audio to text
            return text.lower()  # Return text in lowercase for case-insensitive comparison
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError:
        print("Could not request results. Check your internet connection.")

def load_profanity_list(file_path):
    # Load profanity words from text file
    profanity_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            word = line.strip().lower()
            if word:  # Check if the line is not empty
                profanity_list.append(word)
    return profanity_list

def contains_profanity(text, profanity_list):
    # Check for profane words
    for word in profanity_list:
        if word in text:
            return True
    return False

def write_to_csv(output_file, filename, transcription, profanity_detected):
    # Write to CSV file
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([filename, transcription, profanity_detected])

def main():
    # Define the directory paths and profanity text file path
    audio_dir = r'C:\Users\iMac SSD Win10\Desktop\Profane Words\Ziad Dataset\wav'
    profanity_file = r'C:\Users\iMac SSD Win10\Desktop\Profane Words\bad-words.txt'
    output_file = r'C:\Users\iMac SSD Win10\Desktop\Profane Words\profanity_results.csv'
    
    # Load profanity words from text file
    profanity_list = load_profanity_list(profanity_file)
    
    if not profanity_list:
        return  # Exit if profanity list could not be loaded
    
    # Write CSV header
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File Name', 'Transcribed Text', 'Profanity Detected'])
    
    # Initialize counters for accuracy calculation
    total_files = 0
    profanity_detected_files = 0
    
    # Iterate through audio files in the directory
    for filename in os.listdir(audio_dir):
        if filename.endswith(".wav"):  # Check for .wav files
            file_path = os.path.join(audio_dir, filename)
            print(f"Transcribing and checking profanity in {filename}...")
            
            # Transcribe audio
            transcription = transcribe_audio(file_path)
            
            if transcription:
                # Check for profanity
                profanity_detected = contains_profanity(transcription, profanity_list)
                
                if profanity_detected:
                    print(f"Profanity detected in {filename}")
                    profanity_detected_files += 1
                
                # Write result to CSV
                write_to_csv(output_file, filename, transcription, "Yes" if profanity_detected else "No")
                
                total_files += 1
            else:
                print(f"Unable to transcribe {filename}")
    
    # Calculate accuracy
    if total_files > 0:
        accuracy = (profanity_detected_files / total_files) * 100
        print(f"\nProfanity detection summary:")
        print(f"Total number of audio files processed: {total_files}")
        print(f"Number of files with profanity detected: {profanity_detected_files}")
        print(f"Profanity detection accuracy: {accuracy:.2f}%")
    else:
        print("No audio files processed.")
        

if __name__ == "__main__":
    main()
