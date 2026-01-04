import sys
import os
import time
import re

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    import pyttsx3
    import pythoncom
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

from src.core.tts import SpeechEngine

def clean_for_tts(text):
    # The logic from helpers.py
    text = re.sub(r'[^\w\s,?.!\':-]', '', text)
    return text.strip()

def test_time_speech():
    print("Initializing SpeechEngine...")
    engine = SpeechEngine()
    engine.start()
    
    # Test specific time string
    raw_response = "It's currently 9:16 PM 🕒"
    cleaned = clean_for_tts(raw_response)
    print(f"Raw: '{raw_response}'")
    print(f"Cleaned: '{cleaned}'")
    
    print(f"Queueing: {cleaned}")
    engine.speak(cleaned)
    
    # Wait loop to simulate main thread doing other things
    for i in range(10):
        print(f"Main thread waiting... {i}")
        time.sleep(0.5)
    
    print("Stopping engine...")
    engine.stop()
    print("Test complete.")

if __name__ == "__main__":
    test_time_speech()
