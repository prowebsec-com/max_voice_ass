import time
import logging
import threading
import colorama
from colorama import Fore, Style
from src.core.tts import SpeechEngine
from src.core.stt import Ear
from src.core.brain import Brain
from src.utils.helpers import clean_for_tts
from src.config import WAKE_WORD
from src.ui.gui import MaxGUI

# Setup logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

def assistant_thread(gui, tts):
    """
    Runs the main assistant loop in a separate thread.
    Updates the GUI safely.
    """
    colorama.init(autoreset=True)
    
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════╗
    ║        MAX VOICE ASSISTANT 🤖        ║
    ║   (Offline/Hybrid Intelligence)      ║
    ╚══════════════════════════════════════╝
    """)
    print(Fore.WHITE + "Initializing systems...")
    
    gui.after(0, lambda: gui.update_status("Initializing...", "#ffff00"))

    # Initialize components
    try:
        # TTS is passed in
        
        ear = Ear()
        if not ear.microphone:
            print(Fore.RED + "CRITICAL: No microphone found. Exiting.")
            gui.after(0, lambda: gui.update_status("Mic Error", "#ff0000"))
            return

        brain = Brain()
        
        print(Fore.GREEN + f"\n✓ System Ready! Always listening for commands.")
        
        # Initial greeting
        tts.speak(f"Hello! I am {brain.name}. I am listening.")
        
        # --- STATE MACHINE DEFINITION ---
        # User requested continuous listening mode (No Wake Word)
        
        while True:
            try:
                # --- CONTINUOUS LISTENING LOOP ---
                gui.after(0, lambda: gui.update_status("Listening...", "#ff4444"))
                gui.after(0, lambda: gui.set_visualizer("listening"))
                
                # Listen for command (longer timeout, loop until heard)
                text = ear.listen(timeout=None, phrase_time_limit=5)
                
                if text:
                    print(Fore.WHITE + f"User: {text}")
                    gui.after(0, lambda: gui.add_message("User", text))
                    
                    # Process Command
                    gui.after(0, lambda: gui.update_status("Thinking...", "#00ccff"))
                    gui.after(0, lambda: gui.set_visualizer("processing"))
                    
                    response = brain.think(text)
                    
                    if response:
                        print(Fore.CYAN + f"Max: {response}")
                        gui.after(0, lambda: gui.add_message("Max", response))
                        
                        gui.after(0, lambda: gui.set_visualizer("speaking"))
                        tts.speak(clean_for_tts(response))
                        
                        # Wait for speech to finish before listening again
                        # This prevents "listening to itself" and audio conflicts
                        tts.wait_until_done()
                        
                        if "goodbye" in response.lower():
                            time.sleep(2)
                            gui.quit_app()
                            break
                else:
                    # Silence or unrecognized noise
                    pass
                
                # Loop immediately back to listening
                
            except Exception as e:
                print(Fore.RED + f"Error in loop: {e}")
                logging.error(f"Loop error: {e}")
                time.sleep(1) # Prevent rapid error looping

    except Exception as e:
        print(Fore.RED + f"\nCritical error: {e}")
        logging.exception(e)
        gui.after(0, lambda: gui.add_message("Error", str(e)))
    finally:
        print(Fore.RED + "System Offline.")

def main():
    # 1. Create the GUI
    app = MaxGUI()
    
    # 2. Start TTS Engine in Main Thread Context (passed to worker)
    tts = SpeechEngine()
    tts.start()

    # 3. Start the assistant in a separate thread
    t = threading.Thread(target=assistant_thread, args=(app, tts), daemon=True)
    t.start()
    
    # 4. Run the GUI main loop
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        tts.stop()

if __name__ == "__main__":
    main()
