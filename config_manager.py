import json
import os
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class AppConfig:
    playback_speed: float = 1.0
    repeat_count: int = 1
    force_stop_key: str = "q"  # Tecla para Ctrl+Key
    record_start_key: str = "f9"
    record_stop_key: str = "f10"
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    def save(self, filepath: str = "config.json"):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4)
    
    @classmethod
    def load(cls, filepath: str = "config.json") -> "AppConfig":
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return cls.from_dict(json.load(f))
            except:
                return cls()
        return cls()