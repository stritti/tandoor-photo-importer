import logging
from abc import ABC, abstractmethod

# Logger konfigurieren
logger = logging.getLogger('ai_service')

class BaseAIProvider(ABC):
    """Basisklasse für alle AI-Provider"""
    
    @property
    @abstractmethod
    def provider_name(self):
        """Name des Providers"""
        pass
    
    @abstractmethod
    def analyze_image(self, image_path, prompt):
        """
        Analysiert ein Bild mit dem AI-Provider
        
        Args:
            image_path: Pfad zur Bilddatei
            prompt: Anweisung/Frage an die KI
            
        Returns:
            dict: Ergebnis der Analyse
        """
        pass
    
    def _create_error_response(self, error_message):
        """Erstellt eine standardisierte Fehlerantwort"""
        return {
            "provider": self.provider_name,
            "error": error_message
        }
    
    def _create_success_response(self, response_text, model=None):
        """Erstellt eine standardisierte Erfolgsantwort"""
        result = {
            "provider": self.provider_name,
            "response": response_text
        }
        if model:
            result["model"] = model
        return result
