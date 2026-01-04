import speech_recognition as sr
import logging

class Ear:
    """
    Handles Speech-to-Text using speech_recognition.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except OSError:
            logging.error("No microphone detected! Please check your audio settings.")
            self.microphone = None
        
        if self.microphone:
            self.adjust_mic()

    def adjust_mic(self):
        """Calibrates microphone for ambient noise."""
        if not self.microphone:
            return
        
        try:
            with self.microphone as source:
                logging.info("Calibrating microphone... (Silence please)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logging.info("Microphone calibrated.")
        except Exception as e:
            logging.error(f"Error adjusting microphone: {e}")

    def listen(self, timeout=5, phrase_time_limit=5):
        """
        Listens for audio and converts it to text.
        Returns lowercase text or None if nothing heard/understood.
        """
        if not self.microphone:
            return None

        try:
            with self.microphone as source:
                # logging.debug("Listening...") # Reduced noise
                # timeout: seconds to wait for speech to start
                # phrase_time_limit: max seconds to record
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            try:
                # Using Google Speech Recognition (Free, Online)
                # It's the most reliable free option without complex setup
                text = self.recognizer.recognize_google(audio)
                return text.lower()
            except sr.UnknownValueError:
                # Speech was unintelligible
                return None
            except sr.RequestError as e:
                logging.error(f"Network error (Speech API): {e}")
                return "offline_error"
                
        except sr.WaitTimeoutError:
            # Silence
            return None
        except Exception as e:
            logging.error(f"Listening error: {e}")
            return None
