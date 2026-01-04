# Max Voice Assistant 🤖

A high-level, offline-first smart voice assistant built with Python. Max is designed to be friendly, emotional, and reliable, running on Windows with free tools.

## Features
- **Voice Activation**: Wakes up to "Hey Max".
- **Emotional Intelligence**: Responds with personality and emojis.
- **Hybrid Intelligence**: 
  - Offline: Commands, small talk, time/date, app launching.
  - Online: Wikipedia fallback for definitions and questions.
- **Thread-safe**: Non-blocking Text-to-Speech (TTS).
- **Extensible**: Modular design for adding new skills.

## Architecture
The project follows a clean, modular structure:

- **`main.py`**: The entry point. Manages the State Machine (Sleep -> Wake -> Listen -> Respond).
- **`src/core/brain.py`**: The intelligence center. Routes commands, manages memory, and generates emotional responses.
- **`src/core/ear.py`**: Handles Speech-to-Text using `speech_recognition` (Google API free tier).
- **`src/core/tts.py`**: Handles Text-to-Speech using `pyttsx3` in a separate thread to prevent freezing.
- **`src/config.py`**: Configuration for names, wake words, and voice settings.

## Setup & Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: On Windows, you might need to install PyAudio binary if pip fails (usually `pip install pyaudio` works).*

2. **Run Max**:
   ```bash
   python main.py
   ```

3. **Usage**:
   - Wait for "System Ready".
   - Say **"Hey Max"**.
   - Max will reply "Yeah?".
   - Say a command like **"Open Notepad"**, **"Tell me a joke"**, or **"Who is Elon Musk?"**.
   - Say **"Goodbye"** to exit.

## Extending Max 🚀

To add new commands, edit `src/core/brain.py`.

**Example: Add a "Coin Flip" feature**
1. Import `random` in `brain.py`.
2. Add this block inside `_match_command`:

```python
if "flip a coin" in text:
    result = random.choice(["Heads", "Tails"])
    return f"It's {result}! 🪙"
```

## Troubleshooting
- **Microphone Error**: Ensure your microphone is set as the default recording device in Windows Sound Settings.
- **Speech Not Recognized**: Max uses Google Speech Recognition. An internet connection is required for high accuracy. If offline, it might fail unless you configure an offline engine (like Vosk).
- **TTS Voice**: Max tries to select a friendly voice (Zira on Windows). You can change this in `src/core/tts.py`.
