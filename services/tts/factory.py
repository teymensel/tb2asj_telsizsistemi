from .edge_provider import EdgeTTSProvider
from .google_provider import GoogleTTSProvider
from .system_provider import SystemTTSProvider

class TTSFactory:
    @staticmethod
    def get_providers():
        return [
            EdgeTTSProvider(),
            GoogleTTSProvider(),
            SystemTTSProvider()
        ]
        
    @staticmethod
    def create_provider(name: str):
        if name == "Edge TTS (Microsoft)":
            return EdgeTTSProvider()
        elif name == "Google TTS":
            return GoogleTTSProvider()
        else:
            return SystemTTSProvider()
