import tkinter as tk
from tkinter import ttk
import threading
import math
from src.config import ASSISTANT_NAME

class MaxGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(ASSISTANT_NAME)
        # Compact Size
        self.geometry("300x450")
        self.resizable(False, False)
        
        # Always on top
        self.attributes('-topmost', True)
        
        # Modern Dark Theme Colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#007acc"
        self.secondary_bg = "#252526"
        self.highlight_color = "#3e3e42"
        
        self.configure(bg=self.bg_color)
        
        # Remove default title bar
        self.overrideredirect(True) 
        
        # --- Custom Title Bar ---
        self.title_bar = tk.Frame(self, bg=self.secondary_bg, relief="flat", bd=0, height=30)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False) # Prevent shrinking
        
        self.title_label = tk.Label(self.title_bar, text=f"🤖 {ASSISTANT_NAME}", bg=self.secondary_bg, fg=self.fg_color, font=("Segoe UI", 9, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        self.close_button = tk.Label(self.title_bar, text="✕", bg=self.secondary_bg, fg=self.fg_color, font=("Arial", 10), cursor="hand2")
        self.close_button.pack(side=tk.RIGHT, padx=10)
        self.close_button.bind("<Button-1>", lambda e: self.quit_app())
        self.close_button.bind("<Enter>", lambda e: self.close_button.config(fg="#ff5555"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.config(fg=self.fg_color))

        self.minimize_button = tk.Label(self.title_bar, text="─", bg=self.secondary_bg, fg=self.fg_color, font=("Arial", 10, "bold"), cursor="hand2")
        self.minimize_button.pack(side=tk.RIGHT, padx=5)
        self.minimize_button.bind("<Button-1>", lambda e: self.minimize_app())
        self.minimize_button.bind("<Enter>", lambda e: self.minimize_button.config(fg=self.accent_color))
        self.minimize_button.bind("<Leave>", lambda e: self.minimize_button.config(fg=self.fg_color))
        
        # Bind dragging events
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        
        # --- Main Content ---
        
        # Status Label
        self.status_label = tk.Label(self, text="Initializing...", bg=self.bg_color, fg=self.accent_color, font=("Segoe UI", 12))
        self.status_label.pack(pady=(15, 5))
        
        # Canvas for Visualizer Animation
        self.canvas_width = 300
        self.canvas_height = 60
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(pady=5)
        
        # Animation State
        self.anim_state = "sleeping" # sleeping, listening, speaking, processing
        self.anim_frame = 0
        self.is_animating = True
        self.start_animation()

        # Conversation Log
        self.chat_frame = tk.Frame(self, bg=self.bg_color)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_log = tk.Text(self.chat_frame, bg=self.secondary_bg, fg=self.fg_color, font=("Segoe UI", 9), bd=0, state='disabled', wrap=tk.WORD, padx=5, pady=5)
        self.chat_log.pack(fill=tk.BOTH, expand=True)
        
        # Initial position vars
        self.x = 0
        self.y = 0

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def update_status(self, text, color=None):
        if color:
            self.status_label.config(text=text, fg=color)
        else:
            self.status_label.config(text=text)
            
    def set_visualizer(self, state):
        self.anim_state = state

    def add_message(self, sender, text):
        self.chat_log.config(state='normal')
        
        if sender == "Max":
            self.chat_log.insert(tk.END, f"\n{sender}: {text}\n", "max")
            self.chat_log.tag_config("max", foreground="#00ccff", font=("Segoe UI", 9, "bold"))
        elif sender == "System":
            self.chat_log.insert(tk.END, f"\n[System]: {text}\n", "sys")
            self.chat_log.tag_config("sys", foreground="#777777", font=("Segoe UI", 8, "italic"))
        else:
            self.chat_log.insert(tk.END, f"\nYou: {text}\n", "user")
            self.chat_log.tag_config("user", foreground="#aaaaaa")
            
        self.chat_log.see(tk.END)
        self.chat_log.config(state='disabled')

    def quit_app(self):
        self.is_animating = False
        self.destroy()
        import os
        os._exit(0)

    def minimize_app(self):
        # Minimize the window
        # Note: With overrideredirect(True), standard iconify might behave differently depending on OS.
        # This approach works on most Windows setups.
        self.overrideredirect(False)
        self.iconify()
        self.bind("<Map>", self.restore_app)

    def restore_app(self, event):
        if self.state() == "normal":
            self.overrideredirect(True)
            self.unbind("<Map>")

    def start_animation(self):
        if not self.is_animating:
            return
            
        self.canvas.delete("all")
        width = self.canvas_width
        height = self.canvas_height
        center_y = height / 2
        
        # Colors
        color_map = {
            "sleeping": "#555555",
            "listening": "#ff4444",
            "speaking": "#00ccff",
            "processing": "#ffff00"
        }
        color = color_map.get(self.anim_state, "#555555")
        
        # Draw 3 circles
        for i in range(3):
            # Calculate pulsing size
            offset = i * 2 # Phase shift
            t = (self.anim_frame + offset) % 20
            
            if self.anim_state == "sleeping":
                radius = 5
            elif self.anim_state == "listening":
                # Fast Pulse
                pulse = math.sin(self.anim_frame * 0.5 + i) * 5
                radius = 8 + pulse
            elif self.anim_state == "speaking":
                # Wave
                pulse = math.sin(self.anim_frame * 0.8 + i) * 8
                radius = 10 + pulse
            elif self.anim_state == "processing":
                 # Rotate/Loading feel (simulated by size)
                 pulse = math.cos(self.anim_frame * 0.4 + i) * 4
                 radius = 6 + pulse
            else:
                radius = 5
                
            # Spacing
            cx = width/2 + (i - 1) * 40
            
            self.canvas.create_oval(cx - radius, center_y - radius, cx + radius, center_y + radius, fill=color, outline="")

        self.anim_frame += 1
        self.after(50, self.start_animation) # 20 FPS

    def run(self):
        self.mainloop()
