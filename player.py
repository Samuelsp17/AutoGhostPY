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
        # Proteção contra None ou valores inválidos
        if not key_str or not isinstance(key_str, str):
            return None
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
            'Key.f13': Key.f13,
            'Key.f14': Key.f14,
            'Key.f15': Key.f15,
            'Key.f16': Key.f16,
            'Key.f17': Key.f17,
            'Key.f18': Key.f18,
            'Key.f19': Key.f19,
            'Key.f20': Key.f20,
            'Key.caps_lock': Key.caps_lock,
            'Key.num_lock': Key.num_lock,
            'Key.scroll_lock': Key.scroll_lock,
            'Key.print_screen': Key.print_screen,
            'Key.pause': Key.pause,
            'Key.menu': Key.menu,
            # Teclas específicas do numpad (não duplicadas)
            'Key.clear': None,    # Num 5 (centro) - não disponível no pynput  
        }
        
        # Se estiver no mapa, retorna o objeto Key
        if key_str in key_map:
            return key_map[key_str]
        
        # Se começar com 'Key.', tenta pegar dinamicamente
        if key_str.startswith('Key.'):
            # Teclas que sabemos que não existem
            if key_str == 'Key.clear':
                return None  # Ignora Num 5 do centro quando NumLock desligado
            
            try:
                key_name = key_str.replace('Key.', '')
                return getattr(Key, key_name)
            except AttributeError:
                print(f"Tecla não reconhecida: {key_str}")
                return None
        
        # Se for código VK numérico do numpad (VK_NUMPAD0 = 96 até VK_NUMPAD9 = 105)
        if key_str.isdigit():
            code = int(key_str)
            if 96 <= code <= 105:  # Numpad 0-9
                # Retorna o caractere numérico correspondente
                return chr(ord('0') + (code - 96))
            elif code == 110:  # VK_DECIMAL - Numpad .
                return '.'
            elif code == 106:  # VK_MULTIPLY - Numpad *
                return '*'
            elif code == 107:  # VK_ADD - Numpad +
                return '+'
            elif code == 109:  # VK_SUBTRACT - Numpad -
                return '-'
            elif code == 111:  # VK_DIVIDE - Numpad /
                return '/'
        
        # Caractere normal (letra/número)
        return key_str
        
    
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
            if key is None:
                return  # Ignora teclas desconhecidas
            if isinstance(key, str):
                self.keyboard.press(key)
            else:
                self.keyboard.press(key)
                
        elif event_type == "key_release":
            key = self._parse_key(event["key"])
            if key is None:
                return  # Ignora teclas desconhecidas
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