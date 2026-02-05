from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class TTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Provider name"""
        pass
        
    @abstractmethod
    def get_voices(self) -> List[Dict]:
        """List available voices"""
        pass
        
    @abstractmethod
    def set_voice(self, voice_id: str):
        """Set current voice"""
        pass
        
    @abstractmethod
    def speak(self, text: str, output_file: str) -> bool:
        """Generate audio file from text. Returns True if successful."""
        pass
