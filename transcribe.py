#!/usr/bin/env python3

import speech_recognition as sr
from os import path

AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "test.wav")
TRANSCRIPTION_FILE = path.join(path.dirname(path.realpath(__file__)), "transcription.txt")

def transcribe_audio(wav_file_path):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(wav_file_path) as source:
            audio = r.listen(source)
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Speech Recognition service; {e}"
    except FileNotFoundError:
        return f"Error: The file '{wav_file_path}' was not found."
    except Exception as e:
            return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    transcription = transcribe_audio(AUDIO_FILE)
    print(transcription)
    with open(TRANSCRIPTION_FILE, "w", encoding="utf-8") as file:
        file.write(transcription)