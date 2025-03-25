import base64
import logging
import traceback
from decouple import config
import anthropic

from .base_provider import BaseAIProvider

# Konfiguration aus Umgebungsvariablen
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
ANTHROPIC_MODEL = config('ANTHROPIC_MODEL', default='claude-3-opus-20240229')
MAX_TOKENS = config('MAX_TOKENS', default=300, cast=int)

# Logger
logger = logging.getLogger('ai_service')

class AnthropicProvider(BaseAIProvider):
    """Provider für Anthropic Claude API"""
    
    @property
    def provider_name(self):
        return "anthropic"
    
    def analyze_image(self, image_path, prompt):
        """Analysiert ein Bild mit Anthropic Claude API"""
        if not ANTHROPIC_API_KEY:
            logger.error("Anthropic API-Schlüssel nicht konfiguriert")
            return self._create_error_response("Anthropic API-Schlüssel nicht konfiguriert")
        
        try:
            logger.info("Starte Anthropic Claude Bildanalyse")
            logger.debug(f"Verwende Anthropic Modell: {ANTHROPIC_MODEL}")
            logger.debug(f"Max Tokens: {MAX_TOKENS}")
            
            # Bild in base64 konvertieren und Medientyp bestimmen
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Medientyp basierend auf Dateiendung bestimmen
                media_type = self._determine_media_type(image_path)
            
            # Initialisiere den Anthropic-Client
            logger.info("Initialisiere Anthropic Client")
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            
            logger.info(f"Sende Anfrage an Anthropic API mit Medientyp: {media_type}")
            message = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64_image}}
                        ]
                    }
                ]
            )
            
            logger.info("Antwort von Anthropic API erhalten")
            
            return self._create_success_response(
                message.content[0].text,
                ANTHROPIC_MODEL
            )
            
        except Exception as e:
            logger.error(f"Fehler bei Anthropic Bildanalyse: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._create_error_response(str(e))
    
    def _determine_media_type(self, image_path):
        """Bestimmt den MIME-Typ basierend auf der Dateiendung"""
        media_type = "image/jpeg"  # Standard
        if image_path.lower().endswith('.png'):
            media_type = "image/png"
        elif image_path.lower().endswith('.gif'):
            media_type = "image/gif"
        return media_type
