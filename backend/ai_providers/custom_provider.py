import logging
import traceback
import requests
from decouple import config

from base_provider import BaseAIProvider

# Konfiguration aus Umgebungsvariablen
CUSTOM_API_URL = config('CUSTOM_API_URL', default='')
CUSTOM_API_KEY = config('CUSTOM_API_KEY', default='')

# Logger
logger = logging.getLogger('ai_service')

class CustomProvider(BaseAIProvider):
    """Provider für benutzerdefinierte API"""
    
    @property
    def provider_name(self):
        return "custom"
    
    def analyze_image(self, image_path, prompt):
        """
        Beispiel für die Integration eines benutzerdefinierten API-Dienstes
        Diese Methode kann angepasst werden, um andere KI-Dienste zu unterstützen
        """
        if not CUSTOM_API_URL or not CUSTOM_API_KEY:
            logger.error("Benutzerdefinierte API nicht konfiguriert")
            return self._create_error_response("Benutzerdefinierte API nicht konfiguriert")
        
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
                        "provider": self.provider_name,
                        "response": response.json()
                    }
                else:
                    logger.error(f"Custom API Fehler: {response.status_code} - {response.text}")
                    return self._create_error_response(f"API-Fehler: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Fehler bei Custom API Bildanalyse: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._create_error_response(str(e))
