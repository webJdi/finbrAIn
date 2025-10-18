# src/utils/memory_manager.py
import json
import pickle
from datetime import datetime
from typing import Dict, List, Any

class MemoryManager:
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = memory_file
        self.memories = self._load_memories()
    
    def _load_memories(self) -> Dict[str, Any]:
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_memory(self, key: str, data: Any, timestamp: bool = True):
        if timestamp:
            data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
        self.memories[key] = data
        self._save_memories()
    
    def get_memory(self, key: str) -> Any:
        return self.memories.get(key)
    
    def _save_memories(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)