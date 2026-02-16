import json
import time
import threading
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
from typing import Callable, Optional, Dict


class Player:
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.playing = False
        self.stopped = False
        self.events: list = []
        self.speed: float = 1.0
        self.repeat_count: int = 1
        self._thread: Optional[threading.Thread] = None
        self._on_finish_callback: Optional[Callable] = None
        self._on_stop_callback: Optional[Callable] = None
        
    def load_from_file(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.events = data.get("events", [])
    
    def _parse_key(self, key_str: str):
        """Converte string da tecla para objeto Key"""
        key_map = {
            'Key.space': Key.space,
            'Key.enter': Key.enter,
            'Key.tab': Key.tab,
            'Key.esc': Key.esc,
            'Key.shift': Key.shift,
            'Key.shift_r': Key.shift_r,
            'Key.ctrl': Key.ctrl,
            'Key.ctrl_r': Key.ctrl_r,
            'Key.alt': Key.alt,
            'Key.alt_r': Key.alt_r,
            'Key.cmd': Key.cmd,
            'Key.cmd_r': Key.cmd_r,
            'Key.up': Key.up,
            'Key.down': Key.down,
            'Key.left': Key.left,
            'Key.right': Key.right,
            'Key.home': Key.home,
            'Key.end': Key.end,
            'Key.page_up': Key.page_up,
            'Key.page_down': Key.page_down,
            'Key.delete': Key.delete,
            'Key.backspace': Key.backspace,
            'Key.insert': Key.insert,
            'Key.f1': Key.f1,
            'Key.f2': Key.f2,
            'Key.f3': Key.f3,
            'Key.f4': Key.f4,
            'Key.f5': Key.f5,
            'Key.f6': Key.f6,
            'Key.f7': Key.f7,
            'Key.f8': Key.f8,
            'Key.f9': Key.f9,
            'Key.f10': Key.f10,
            'Key.f11': Key.f11,
            'Key.f12': Key.f12,
            'Key.caps_lock': Key.caps_lock,
            'Key.num_lock': Key.num_lock,
            'Key.scroll_lock': Key.scroll_lock,
        }
        return key_map.get(key_str, key_str)
    
    def _parse_button(self, button_str: str):
        """Converte string do botão para objeto Button"""
        if "left" in button_str:
            return Button.left
        elif "right" in button_str:
            return Button.right
        elif "middle" in button_str:
            return Button.middle
        return Button.left
    
    def _execute_event(self, event: Dict):
        event_type = event.get("type")
        
        if event_type == "mouse_move":
            self.mouse.position = (event["x"], event["y"])
            
        elif event_type == "mouse_click":
            self.mouse.position = (event["x"], event["y"])
            button = self._parse_button(event["button"])
            if event["pressed"]:
                self.mouse.press(button)
            else:
                self.mouse.release(button)
                
        elif event_type == "mouse_scroll":
            self.mouse.scroll(event["dx"], event["dy"])
            
        elif event_type == "key_press":
            key = self._parse_key(event["key"])
            if isinstance(key, str):
                self.keyboard.press(key)
            else:
                self.keyboard.press(key)
                
        elif event_type == "key_release":
            key = self._parse_key(event["key"])
            if isinstance(key, str):
                self.keyboard.release(key)
            else:
                self.keyboard.release(key)
    
    def _play_once(self):
        if not self.events:
            return
        
        start_time = time.time()
        
        for event in self.events:
            if self.stopped:
                break
            
            # Calcula tempo esperado ajustado pela velocidade
            expected_time = event["timestamp"] / self.speed
            current_time = time.time() - start_time
            
            # Espera até o momento correto
            wait_time = expected_time - current_time
            if wait_time > 0:
                time.sleep(wait_time)
            
            self._execute_event(event)
    
    def _play_loop(self):
        for i in range(self.repeat_count):
            if self.stopped:
                break
            self._play_once()
        
        self.playing = False
        
        if self._on_finish_callback and not self.stopped:
            self._on_finish_callback()
    
    def play(self):
        if not self.events or self.playing:
            return
        
        self.playing = True
        self.stopped = False
        self._thread = threading.Thread(target=self._play_loop)
        self._thread.start()
    
    def stop(self):
        self.stopped = True
        self.playing = False
        
        if self._on_stop_callback:
            self._on_stop_callback()
    
    def set_on_finish_callback(self, callback: Callable):
        self._on_finish_callback = callback
    
    def set_on_stop_callback(self, callback: Callable):
        self._on_stop_callback = callback