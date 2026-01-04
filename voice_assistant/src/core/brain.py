import random
import datetime
import subprocess
import wikipedia
import logging
import pywhatkit
import google.generativeai as genai
import os
from AppOpener import open as open_app
from collections import deque
from src.config import ASSISTANT_NAME, GEMINI_API_KEY

class Brain:
    """
    The intelligence center of the assistant.
    Handles command routing, context, and response generation.
    """
    def __init__(self):
        self.name = ASSISTANT_NAME
        self.memory = deque(maxlen=5) # Keep track of last 5 interactions
        
        self.has_gemini = False
        api_key = (GEMINI_API_KEY or "").strip()
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                try:
                    _ = self.model.generate_content("hello")
                    self.chat_session = self.model.start_chat(history=[])
                    self.has_gemini = True
                except Exception as e:
                    logging.error(f"Gemini Verify Error: {e}")
            except Exception as e:
                logging.error(f"Gemini Init Error: {e}")
        
    def think(self, text):
        """
        Process the input text and return a response.
        """
        if not text:
            return None
            
        text = text.lower()
        self.memory.append(f"User: {text}")
        
        response = self._match_command(text)
        
        if not response:
            response = self._chat_with_ai(text)
        if not response:
            response = self._knowledge_fallback(text)
        if not response:
            response = self._smalltalk_fallback(text)
        
        self.memory.append(f"Max: {response}")
        return response

    def _chat_with_ai(self, text):
        if not self.has_gemini:
            return None
        try:
            response = self.chat_session.send_message(text)
            return (response.text or "").replace("*", "")
        except Exception:
            return None

    def _match_command(self, text):
        # --- Core Commands ---
        
        # Exit/Quit
        if any(x in text for x in ["exit", "quit", "bye", "goodbye", "sleep", "shutdown"]):
            return "Goodbye! Have a wonderful day! 👋"

        # Greetings
        if any(x in text for x in ["hello", "hi", "hey", "greetings"]):
            return f"Hey there! 😊 How can I help you today?"
            
        # Status check
        if "how are you" in text:
            return f"I'm doing great, thanks for asking! 💙 How about you?"
        if "how old are you" in text:
            return "I'm old enough to be helpful!"
        if any(x in text for x in ["what's up", "whats up", "sup"]):
            return "Just here, ready to help!"
            
        # Identity
        if "your name" in text or "who are you" in text:
            return f"I'm {ASSISTANT_NAME}, your personal AI assistant! 🤖"

        # --- Utilities ---

        # Time
        if "time" in text:
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p").lstrip('0')
            return f"It's currently {time_str} 🕒"

        # Date
        if "date" in text or "day" in text:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today} 📅"

        # Open Apps (Windows) - Generic
        if "open" in text and "settings" not in text:
            app_name = text.replace("open", "").strip()
            if app_name:
                try:
                    # AppOpener is smart enough to find "google chrome" from "chrome"
                    open_app(app_name, match_closest=True, output=False) 
                    return f"Opening {app_name}... 🚀"
                except Exception:
                     # Fallback for built-in tools not indexed by AppOpener sometimes
                    if "notepad" in app_name:
                        subprocess.Popen(["notepad.exe"])
                        return "Opening Notepad."
                    elif "calculator" in app_name:
                        subprocess.Popen(["calc.exe"])
                        return "Opening Calculator."
                    else:
                        return f"I couldn't find an app named {app_name}. 😕"
                
        if "open settings" in text:
            try:
                subprocess.Popen(["start", "ms-settings:"], shell=True)
                return "Opening Settings... ⚙️"
            except Exception:
                return "Could not open settings. 😕"
                
        # Play Music (YouTube)
        if "play" in text:
            song = text.replace("play", "").strip()
            if song:
                try:
                    pywhatkit.playonyt(song)
                    return f"Playing {song} on YouTube 🎶"
                except Exception:
                    return "I had trouble playing that song. 😕"

        return None

    def _knowledge_fallback(self, text):
        triggers = ["who is", "what is", "tell me about", "define", "search for"]
        if any(t in text for t in triggers):
            query = text
            for t in triggers:
                query = query.replace(t, "")
            query = query.strip()
            if not query:
                return None
            try:
                summary = wikipedia.summary(query, sentences=2)
                return f"Here's what I found on Wikipedia: {summary}"
            except Exception:
                return None
        return None

    def _smalltalk_fallback(self, text):
        return "I'm here and listening. Ask me anything."
