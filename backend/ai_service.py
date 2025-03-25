import logging
from ai_providers.provider_factory import AIProviderFactory

# Logger konfigurieren
logging.basicConfig(
    level=logging.WARNING,  # Root-Logger auf WARNING setzen
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Nur für den ai_service Logger INFO-Level aktivieren
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
        
        try:
            # Provider über Factory holen
            provider = AIProviderFactory.get_provider()
            
            # Bild mit dem Provider analysieren
            return provider.analyze_image(image_path, prompt)
            
        except ValueError as e:
            logger.error(f"Fehler beim Erstellen des Providers: {str(e)}")
            return {
                "provider": "none",
                "error": str(e)
            }
