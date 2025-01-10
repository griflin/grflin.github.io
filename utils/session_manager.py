import os
import json
import time
from typing import Dict, Any
from datetime import datetime

class SessionManager:
    def __init__(self, save_dir: str):
        self.save_dir = save_dir
        self.session_data = {
            'start_time': datetime.now().isoformat(),
            'networks': [],
            'attacks': [],
            'results': {}
        }
        self.last_save = time.time()
        os.makedirs(save_dir, exist_ok=True)

    def update(self, key: str, value: Any):
        """Update session data."""
        self.session_data[key] = value
        
    def save(self) -> str:
        """Save session to file."""
        filename = os.path.join(
            self.save_dir,
            f"session_{datetime.now():%Y%m%d_%H%M%S}.json"
        )
        with open(filename, 'w') as f:
            json.dump(self.session_data, f, indent=4)
        self.last_save = time.time()
        return filename

    @classmethod
    def load(cls, filename: str) -> 'SessionManager':
        """Load session from file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        session = cls(os.path.dirname(filename))
        session.session_data = data
        return session 