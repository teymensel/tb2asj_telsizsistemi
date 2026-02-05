import asyncio
import edge_tts
import os
from .base import TTSProvider
from typing import List, Dict

class EdgeTTSProvider(TTSProvider):
    def get_name(self) -> str:
        return "Edge TTS (Microsoft)"
        
    def get_voices(self) -> List[Dict]:
        # Edge TTS sesleri (Statik liste veya dinamik alınabilir)
        # Hız için şimdilik en iyi Türkçe sesleri ekliyorum
        return [
            {'id': 'tr-TR-AhmetNeural', 'name': 'Ahmet (Türkçe)', 'lang': 'tr'},
            {'id': 'tr-TR-EmelNeural', 'name': 'Emel (Türkçe)', 'lang': 'tr'},
            {'id': 'en-US-GuyNeural', 'name': 'Guy (English)', 'lang': 'en'},
            {'id': 'en-US-JennyNeural', 'name': 'Jenny (English)', 'lang': 'en'}
        ]
        
    def set_voice(self, voice_id: str):
        self.current_voice = voice_id
        
    def __init__(self):
        self.current_voice = 'tr-TR-AhmetNeural'
        
    async def _generate(self, text: str, output_file: str):
        communicate = edge_tts.Communicate(text, self.current_voice)
        await communicate.save(output_file)
        
    def speak(self, text: str, output_file: str) -> bool:
        try:
            asyncio.run(self._generate(text, output_file))
            return True
        except Exception as e:
            print(f"EdgeTTS Hatası: {e}")
            return False
