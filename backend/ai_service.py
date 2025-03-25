import os
import base64
import logging
import traceback
import inspect
from decouple import config
import requests
from openai import OpenAI

# Konfiguration aus Umgebungsvariablen
AI_PROVIDER = config('AI_PROVIDER', default='openai')
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4-vision-preview')
MAX_TOKENS = config('MAX_TOKENS', default=300, cast=int)

# Logger konfigurieren
logging.basicConfig(
    level=logging.WARNING,  # Root-Logger auf WARNING setzen
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Nur für den ai_service Logger DEBUG-Level aktivieren
logger = logging.getLogger('ai_service')
logger.setLevel(logging.INFO)

class AIService:
    """Service zur Verarbeitung von Bildern mit verschiedenen KI-Modellen"""
    
    @staticmethod
    def analyze_image(image_path, prompt="Was ist auf diesem Bild zu sehen?"):
        """
        Analysiert ein Bild mit dem konfigurierten KI-Modell
        
        Args:
            image_path: Pfad zur Bilddatei
            prompt: Anweisung/Frage an die KI
            
        Returns:
            dict: Ergebnis der Analyse mit Anbieter und Antwort
        """
        logger.info(f"Starte Bildanalyse mit Prompt: {prompt}")
        logger.info(f"Bildpfad: {image_path}")
        logger.info(f"Konfigurierter AI-Provider: {AI_PROVIDER}")
        
        provider = AI_PROVIDER.lower()
        
        if provider == 'openai':
            logger.info("Verwende OpenAI für die Analyse")
            return AIService._analyze_with_openai(image_path, prompt)
        elif provider == 'custom':
            logger.info("Verwende Custom API für die Analyse")
            return AIService._analyze_with_custom_api(image_path, prompt)
        else:
            logger.error(f"KI-Anbieter '{provider}' nicht unterstützt oder konfiguriert")
            return {
                "provider": "none",
                "error": f"KI-Anbieter '{provider}' nicht unterstützt oder konfiguriert"
            }
    
    @staticmethod
    def _analyze_with_openai(image_path, prompt):
        """Analysiert ein Bild mit OpenAI Vision API"""
        if not OPENAI_API_KEY:
            logger.error("OpenAI API-Schlüssel nicht konfiguriert")
            return {
                "provider": "openai",
                "error": "OpenAI API-Schlüssel nicht konfiguriert"
            }
        
        try:
            logger.info("Starte OpenAI Bildanalyse")
            logger.debug(f"Verwende OpenAI Modell: {OPENAI_MODEL}")
            logger.debug(f"Max Tokens: {MAX_TOKENS}")
            
            # Bild in base64 konvertieren
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                logger.debug(f"Bild erfolgreich in base64 konvertiert")
            
            # Initialisiere den OpenAI-Client
            logger.debug("Initialisiere OpenAI Client")
            logger.debug(f"OpenAI API Key vorhanden: {bool(OPENAI_API_KEY)}")
            
            # Zeige alle verfügbaren Parameter für den OpenAI-Konstruktor
            logger.debug(f"OpenAI.__init__ Parameter: {inspect.signature(OpenAI.__init__)}")
            
            # OpenAI-Client initialisieren
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
            
            result = {
                "provider": "openai",
                "response": response.choices[0].message.content,
                "model": OPENAI_MODEL
            }
            logger.info("OpenAI Bildanalyse erfolgreich abgeschlossen")
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei OpenAI Bildanalyse: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "provider": "openai",
                "error": str(e)
            }
    
    @staticmethod
    def _analyze_with_custom_api(image_path, prompt):
        """
        Beispiel für die Integration eines benutzerdefinierten API-Dienstes
        Diese Methode kann angepasst werden, um andere KI-Dienste zu unterstützen
        """
        CUSTOM_API_URL = config('CUSTOM_API_URL', default='')
        CUSTOM_API_KEY = config('CUSTOM_API_KEY', default='')
        
        if not CUSTOM_API_URL or not CUSTOM_API_KEY:
            logger.error("Benutzerdefinierte API nicht konfiguriert")
            return {
                "provider": "custom",
                "error": "Benutzerdefinierte API nicht konfiguriert"
            }
        
        try:
            logger.info("Starte Custom API Bildanalyse")
            with open(image_path, "rb") as image_file:
                files = {"image": image_file}
                data = {"prompt": prompt}
                headers = {"Authorization": f"Bearer {CUSTOM_API_KEY}"}
                
                logger.info("Sende Anfrage an Custom API")
                response = requests.post(
                    CUSTOM_API_URL,
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info("Custom API Anfrage erfolgreich")
                    return {
                        "provider": "custom",
                        "response": response.json()
                    }
                else:
                    logger.error(f"Custom API Fehler: {response.status_code} - {response.text}")
                    return {
                        "provider": "custom",
                        "error": f"API-Fehler: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Fehler bei Custom API Bildanalyse: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "provider": "custom",
                "error": str(e)
            }
