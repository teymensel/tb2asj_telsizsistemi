import pyttsx3
import os
from .base import TTSProvider
from typing import List, Dict

class SystemTTSProvider(TTSProvider):
    def get_name(self) -> str:
        return "Sistem (Offline)"
        
    def get_voices(self) -> List[Dict]:
        voices_list = []
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            for voice in voices:
                lang = 'Unknown'
                # Dil tespiti
                if hasattr(voice, 'languages') and voice.languages:
                    lang = str(voice.languages[0])
                elif 'turkish' in voice.name.lower() or 'tr' in voice.id.lower():
                    lang = 'tr'
                    
                voices_list.append({
                    'id': voice.id,
                    'name': voice.name,
                    'lang': lang
                })
        except Exception as e:
            print(f"Sistem sesleri alınamadı: {e}")
        return voices_list
        
    def set_voice(self, voice_id: str):
        self.current_voice = voice_id
        
    def __init__(self):
        self.current_voice = None
        
    def speak(self, text: str, output_file: str) -> bool:
        """
        Pyttsx3 output'u dosyaya kaydetmeyi destekler (save_to_file).
        Ancak event loop gerektirir.
        """
        try:
            engine = pyttsx3.init()
            if self.current_voice:
                engine.setProperty('voice', self.current_voice)
            
            # Windows'ta dosya tam yolu gerekebilir
            abs_path = os.path.abspath(output_file)
            engine.save_to_file(text, abs_path)
            engine.runAndWait()
            return True
        except Exception as e:
            print(f"Sistem TTS Hatası: {e}")
            return False
