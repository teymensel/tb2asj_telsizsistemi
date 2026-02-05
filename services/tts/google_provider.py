from gtts import gTTS
from .base import TTSProvider
from typing import List, Dict

class GoogleTTSProvider(TTSProvider):
    def get_name(self) -> str:
        return "Google TTS"
        
    def get_voices(self) -> List[Dict]:
        return [
            {'id': 'tr', 'name': 'Türkçe', 'lang': 'tr'},
            {'id': 'en', 'name': 'English', 'lang': 'en'}
        ]
        
    def set_voice(self, voice_id: str):
        self.current_voice = voice_id
        
    def __init__(self):
        self.current_voice = 'tr'
        
    def speak(self, text: str, output_file: str) -> bool:
        try:
            tts = gTTS(text=text, lang=self.current_voice, slow=False)
            tts.save(output_file)
            return True
        except Exception as e:
            print(f"GoogleTTS Hatası: {e}")
            return False
