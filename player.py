import json
import time
import threading
from pynput.mouse import Controller as MouseController, Button
from typing import Callable, Optional, Dict
import ctypes
from ctypes import wintypes

# Constantes da API do Windows
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# Define ULONG_PTR manualmente para compatibilidade
if ctypes.sizeof(ctypes.c_void_p) == 8:  # 64-bit
    ULONG_PTR = ctypes.c_ulonglong
else:  # 32-bit
    ULONG_PTR = ctypes.c_ulong

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class INPUT_I(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("ii", INPUT_I),
    ]

# Mapa de teclas para códigos VK (Virtual Key)
VK_MAP = {
    # Letras
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46,
    'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
    'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52,
    's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
    'y': 0x59, 'z': 0x5A,
    # Números
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    # Controles
    'ctrl': 0x11, 'control': 0x11, 'ctrl_l': 0xA2, 'ctrl_r': 0xA3,
    'shift': 0x10, 'shift_l': 0xA0, 'shift_r': 0xA1,
    'alt': 0x12, 'alt_l': 0xA4, 'alt_r': 0xA5,
    'win': 0x5B, 'win_r': 0x5C,
    # Especiais
    'space': 0x20, 'enter': 0x0D, 'tab': 0x09, 'esc': 0x1B,
    'backspace': 0x08, 'delete': 0x2E, 'insert': 0x2D,
    'home': 0x24, 'end': 0x23, 'pageup': 0x21, 'pagedown': 0x22,
    'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
    # F1-F12
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
    # Símbolos comuns
    'comma': 0xBC, 'period': 0xBE, 'slash': 0xBF,
    'semicolon': 0xBA, 'quote': 0xDE, 'lbracket': 0xDB,
    'rbracket': 0xDD, 'backslash': 0xDC, 'minus': 0xBD,
    'equal': 0xBB, 'grave': 0xC0,
}

class Player:
    def __init__(self):
        self.mouse = MouseController()
        self.playing = False
        self.stopped = False
        self.events: list = []
        self.speed: float = 1.0
        self.repeat_count: int = 1
        self._thread: Optional[threading.Thread] = None
        self._on_finish_callback: Optional[Callable] = None
        self._on_stop_callback: Optional[Callable] = None
        self._pressed_vk: set = set()  # Códigos VK pressionados
        
        # Carrega função SendInput
        self.SendInput = ctypes.windll.user32.SendInput
        self.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), wintypes.INT]
        self.SendInput.restype = wintypes.UINT
    
    def load_from_file(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.events = data.get("events", [])
    
    def _vk_to_input(self, vk: int, press: bool):
        """Cria estrutura INPUT para uma tecla VK"""
        flags = 0 if press else KEYEVENTF_KEYUP
        ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)
        inp = INPUT(type=INPUT_KEYBOARD, ii=INPUT_I(ki=ki))
        return inp
    
    def _send_key(self, vk: int, press: bool):
        """Envia evento de tecla via SendInput"""
        inp = self._vk_to_input(vk, press)
        self.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    
    def _parse_key(self, key_str: str) -> Optional[int]:
        """Converte string da tecla para código VK"""
        if not key_str or not isinstance(key_str, str):
            return None
        
        key_lower = key_str.lower().replace('key.', '').replace('key_', '')
        
        # Verifica no mapa
        if key_lower in VK_MAP:
            return VK_MAP[key_lower]
        
        # Se for letra/número único
        if len(key_lower) == 1 and key_lower in VK_MAP:
            return VK_MAP[key_lower]
        
        # Códigos VK diretos (numpad)
        if key_str.isdigit():
            code = int(key_str)
            if 96 <= code <= 105:  # Numpad 0-9
                return code
            elif code == 110:  # Numpad .
                return 0x6E
        
        print(f"Tecla não mapeada: {key_str}")
        return None
    
    def _is_modifier(self, vk: int) -> bool:
        """Verifica se é tecla modificadora"""
        return vk in (0x11, 0xA2, 0xA3,  # Ctrl
                      0x10, 0xA0, 0xA1,  # Shift
                      0x12, 0xA4, 0xA5,  # Alt
                      0x5B, 0x5C)         # Win
    
    def _execute_event(self, event: Dict):
        event_type = event.get("type")
        
        if event_type == "mouse_move":
            x, y = event["x"], event["y"]
            self.mouse.position = (x, y)
            # Move o cursor do Windows também
            ctypes.windll.user32.SetCursorPos(x, y)
            
        elif event_type == "mouse_click":
            x, y = event["x"], event["y"]
            pressed = event["pressed"]
            
            ctypes.windll.user32.SetCursorPos(x, y)
            
            # Botões do mouse
            if "left" in event["button"]:
                vk = 0x01  # VK_LBUTTON
            elif "right" in event["button"]:
                vk = 0x02  # VK_RBUTTON
            else:
                vk = 0x04  # VK_MBUTTON
            
            if pressed:
                ctypes.windll.user32.mouse_event(0x0002 if vk == 0x01 else (0x0008 if vk == 0x02 else 0x0020), 0, 0, 0, 0)
            else:
                ctypes.windll.user32.mouse_event(0x0004 if vk == 0x01 else (0x0010 if vk == 0x02 else 0x0040), 0, 0, 0, 0)
                
        elif event_type == "mouse_scroll":
            dy = event.get("dy", 0)
            if dy != 0:
                ctypes.windll.user32.mouse_event(0x0800, 0, 0, dy * 120, 0)
            
        elif event_type == "key_press":
            vk = self._parse_key(event["key"])
            if vk is None:
                return
            
            if self._is_modifier(vk):
                self._pressed_vk.add(vk)
                self._send_key(vk, True)
            else:
                # Pressiona modificadores ativos primeiro (se ainda não estiverem)
                for mod_vk in self._pressed_vk:
                    if mod_vk not in self._pressed_vk:  # Já estão pressionados
                        self._send_key(mod_vk, True)
                
                # Pressiona a tecla principal
                self._send_key(vk, True)
                
        elif event_type == "key_release":
            vk = self._parse_key(event["key"])
            if vk is None:
                return
            
            if self._is_modifier(vk):
                if vk in self._pressed_vk:
                    self._pressed_vk.discard(vk)
                self._send_key(vk, False)
            else:
                # Libera a tecla normal
                self._send_key(vk, False)
    
    def _play_once(self):
        if not self.events:
            return
        
        # Libera todas as teclas antes de começar
        for vk in list(self._pressed_vk):
            self._send_key(vk, False)
        self._pressed_vk.clear()
        
        start_time = time.time()
        
        for event in self.events:
            if self.stopped:
                break
            
            expected_time = event["timestamp"] / self.speed
            current_time = time.time() - start_time
            wait_time = expected_time - current_time
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            self._execute_event(event)
        
        # Libera todas as teclas no final
        for vk in list(self._pressed_vk):
            self._send_key(vk, False)
        self._pressed_vk.clear()
    
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
        # Libera todas as teclas
        for vk in list(self._pressed_vk):
            self._send_key(vk, False)
        self._pressed_vk.clear()
        if self._on_stop_callback:
            self._on_stop_callback()
    
    def set_on_finish_callback(self, callback: Callable):
        self._on_finish_callback = callback
    
    def set_on_stop_callback(self, callback: Callable):
        self._on_stop_callback = callback