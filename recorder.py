import json
import time
import threading
from datetime import datetime
from pynput import mouse, keyboard
from typing import List, Dict, Callable, Optional


class Recorder:
    def __init__(self):
        self.events: List[Dict] = []
        self.recording = False
        self.start_time: Optional[float] = None
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()
        self._on_stop_callback: Optional[Callable] = None
        
    def _get_timestamp(self) -> float:
        return time.time() - self.start_time if self.start_time else 0
    
    def _on_move(self, x, y):
        if self.recording:
            with self._lock:
                self.events.append({
                    "type": "mouse_move",
                    "x": x,
                    "y": y,
                    "timestamp": self._get_timestamp()
                })
    
    def _on_click(self, x, y, button, pressed):
        if self.recording:
            with self._lock:
                self.events.append({
                    "type": "mouse_click",
                    "x": x,
                    "y": y,
                    "button": str(button),
                    "pressed": pressed,
                    "timestamp": self._get_timestamp()
                })
    
    def _on_scroll(self, x, y, dx, dy):
        if self.recording:
            with self._lock:
                self.events.append({
                    "type": "mouse_scroll",
                    "x": x,
                    "y": y,
                    "dx": dx,
                    "dy": dy,
                    "timestamp": self._get_timestamp()
                })
    
    def _on_press(self, key):
        if self.recording:
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key)
            
            with self._lock:
                self.events.append({
                    "type": "key_press",
                    "key": key_str,
                    "timestamp": self._get_timestamp()
                })
    
    def _on_release(self, key):
        if self.recording:
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key)
            
            with self._lock:
                self.events.append({
                    "type": "key_release",
                    "key": key_str,
                    "timestamp": self._get_timestamp()
                })
    
    def start(self):
        self.events = []
        self.recording = True
        self.start_time = time.time()
        
        self.mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
    
    def stop(self):
        self.recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        if self._on_stop_callback:
            self._on_stop_callback()
    
    def save_to_file(self, filepath: str):
        data = {
            "created_at": datetime.now().isoformat(),
            "event_count": len(self.events),
            "events": self.events
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def set_on_stop_callback(self, callback: Callable):
        self._on_stop_callback = callback