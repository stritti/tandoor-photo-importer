import os
import base64
import logging
import traceback
from decouple import config
from openai import OpenAI

from base_provider import BaseAIProvider

# Konfiguration aus Umgebungsvariablen
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4-vision-preview')
MAX_TOKENS = config('MAX_TOKENS', default=300, cast=int)

# Logger
logger = logging.getLogger('ai_service')

class OpenAIProvider(BaseAIProvider):
    """Provider für OpenAI Vision API"""
    
    @property
    def provider_name(self):
        return "openai"
    
    def analyze_image(self, image_path, prompt):
        """Analysiert ein Bild mit OpenAI Vision API"""
        if not OPENAI_API_KEY:
            logger.error("OpenAI API-Schlüssel nicht konfiguriert")
            return self._create_error_response("OpenAI API-Schlüssel nicht konfiguriert")
        
        try:
            logger.info("Starte OpenAI Bildanalyse")
            logger.debug(f"Verwende OpenAI Modell: {OPENAI_MODEL}")
            logger.debug(f"Max Tokens: {MAX_TOKENS}")
            
            # Bild in base64 konvertieren
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Initialisiere den OpenAI-Client
            logger.info("Initialisiere OpenAI Client")
            
            # OpenAI-Client initialisieren
            client = self._initialize_client()
            
            logger.info("Sende Anfrage an OpenAI API")
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=MAX_TOKENS
            )
            logger.info("Antwort von OpenAI API erhalten")
            
            return self._create_success_response(
                response.choices[0].message.content,
                OPENAI_MODEL
            )
            
        except Exception as e:
            logger.error(f"Fehler bei OpenAI Bildanalyse: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._create_error_response(str(e))
    
    def _initialize_client(self):
        """Initialisiert den OpenAI-Client mit verschiedenen Fallback-Methoden"""
        client = None
        try:
            # Methode 1: Nur mit API-Key
            client = OpenAI(api_key=OPENAI_API_KEY)
        except TypeError as e:
            # Methode 2: Setze Umgebungsvariable und initialisiere ohne Parameter
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            try:
                client = OpenAI()
            except Exception:
                # Methode 3: Verwende nur die notwendigsten Parameter
                try:
                    client = OpenAI(
                        api_key=OPENAI_API_KEY,
                        max_retries=2
                    )
                except Exception as e3:
                    logger.error(f"Alle Initialisierungsmethoden fehlgeschlagen: {str(e3)}")
                    raise Exception("Konnte OpenAI-Client nicht initialisieren")
        
        if not client:
            logger.error("OpenAI Client konnte nicht initialisiert werden")
            raise Exception("OpenAI Client ist None nach Initialisierungsversuchen")
            
        return client
