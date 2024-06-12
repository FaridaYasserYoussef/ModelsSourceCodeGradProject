import os
import csv
import speech_recognition as sr
from transformers import pipeline

def speech_to_text(file_path):
    # Initialize recognizer class (for recognizing speech)
    recognizer = sr.Recognizer()

    # Load audio file
    with sr.AudioFile(file_path) as source:
        # Read the audio data
        audio_data = recognizer.record(source)

        try:
            # Recognize the speech using Google Speech Recognition
            text = recognizer.recognize_google(audio_data)
            return text

        except sr.UnknownValueError:
            print(f"Speech recognition could not understand the audio file: {file_path}")
            return None

        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

def perform_sentiment_analysis(text):
    # Initialize sentiment analysis pipeline
    sentiment_analysis = pipeline("sentiment-analysis")

    # Perform sentiment analysis on the provided text
    results = sentiment_analysis(text)

    return results

# Folder path containing .wav files
folder_path = r"C:\Users\iMac SSD Win10\Desktop\Desktop\s2 y3\Grad Proj\New Part Grad Proj\Sentimental analysis\TRAIN"

# Initialize empty list to store results
sentiment_results = []

# Iterate over each file in the folder
for filename in sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else float('inf')):
    if filename.endswith(".wav"):
        file_path = os.path.join(folder_path, filename)
        
        # Perform speech-to-text conversion
        transcribed_text = speech_to_text(file_path)

        if transcribed_text:
            # Perform sentiment analysis on the transcribed text
            results = perform_sentiment_analysis(transcribed_text)
            
            # Determine sentiment label and score
            if results:
                # Get the sentiment label with the highest score
                sentiment_label = results[0]["label"]
                sentiment_score = results[0]["score"]
                
                # Store filename, transcribed text, sentiment label, and sentiment score
                sentiment_results.append({
                    "filename": filename,
                    "transcribed_text": transcribed_text,
                    "sentiment_label": sentiment_label,
                    "sentiment_score": sentiment_score
                })

# Define CSV file path for exporting results
output_csv_path = "sentiment_analysis_results.csv"

# Write sentiment analysis results to CSV file
with open(output_csv_path, "w", newline="") as csv_file:
    fieldnames = ["filename", "transcribed_text", "sentiment_label", "sentiment_score"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    # Sort sentiment results by filename before writing to CSV
    sorted_sentiment_results = sorted(sentiment_results, key=lambda x: int(x["filename"].split('.')[0]))

    for result in sorted_sentiment_results:
        writer.writerow({
            "filename": result["filename"],
            "transcribed_text": result["transcribed_text"],
            "sentiment_label": result["sentiment_label"],
            "sentiment_score": result["sentiment_score"]
        })

print(f"Sentiment analysis results exported to: {output_csv_path}")
