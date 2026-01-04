import pyttsx3
import threading
import queue
import logging
import pythoncom
import time
from src.config import VOICE_RATE, VOICE_VOLUME

class SpeechEngine:
    """
    Thread-safe Text-to-Speech Engine.
    Uses a queue to handle speech requests without blocking the main thread.
    """
    def __init__(self):
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._is_running = False
        self._engine = None # Initialized in the thread
        self.is_speaking = False # Thread-safe flag

    def start(self):
        """Starts the TTS processing thread."""
        if not self._is_running:
            self._is_running = True
            self._thread.start()
            print("TTS Engine started.")

    def speak(self, text):
        """Adds text to the speech queue."""
        if not text:
            return
        self._queue.put(text)
     
    def wait_until_done(self):
        """Blocks until the queue is empty and speech is finished."""
        self._queue.join()
        while self.is_speaking:
            pass # Busy wait, but short duration
        pass

    def _init_engine(self):
        try:
            self._engine = pyttsx3.init('sapi5')
        except Exception:
            try:
                self._engine = pyttsx3.init()
            except Exception:
                self._engine = None
        if self._engine:
            self._engine.setProperty('rate', VOICE_RATE)
            self._engine.setProperty('volume', VOICE_VOLUME)
            try:
                voices = self._engine.getProperty('voices')
                if isinstance(voices, list) and len(voices) > 1:
                    self._engine.setProperty('voice', voices[1].id)
            except Exception:
                pass
            print("TTS Engine initialized successfully in thread.")
            return True
        print("Failed to initialize TTS engine.")
        return False

    def _run_loop(self):
        """Internal loop to process the speech queue."""
        # CRITICAL FIX: Initialize COM for this thread
        try:
            pythoncom.CoInitialize()
        except Exception as e:
            print(f"TTS Thread CoInitialize Warning: {e}")

        self._init_engine()

        while True:
            text = self._queue.get()
            if text is None:
                break
            
            if not self._engine:
                ok = self._init_engine()
                if not ok:
                    time.sleep(0.2)
                    self._queue.task_done()
                    self._queue.put(text)
                    continue
            
            try:
                print(f"TTS Speaking: {text[:20]}...")
                self.is_speaking = True
                if self._engine:
                    self._engine.say(text)
                    self._engine.runAndWait()
            except Exception as e:
                print(f"Error during speech: {e}")
                # Try to re-initialize if engine crashed
                try:
                    self._engine = pyttsx3.init('sapi5')
                    self._engine.setProperty('rate', VOICE_RATE)
                    self._engine.setProperty('volume', VOICE_VOLUME)
                except:
                    pass
            finally:
                self.is_speaking = False
                self._queue.task_done()
        
        # Cleanup
        try:
            pythoncom.CoUninitialize()
        except:
            pass

    def stop(self):
        """Stops the TTS loop."""
        self._queue.put(None)
        if self._thread.is_alive():
            self._thread.join()
