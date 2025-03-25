import logging
from decouple import config

from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .custom_provider import CustomProvider

# Konfiguration aus Umgebungsvariablen
AI_PROVIDER = config('AI_PROVIDER', default='openai')

# Logger
logger = logging.getLogger('ai_service')

class AIProviderFactory:
    """Factory-Klasse zur Erstellung von AI-Providern"""
    
    @staticmethod
    def get_provider():
        """
        Gibt eine Instanz des konfigurierten AI-Providers zurück
        
        Returns:
            BaseAIProvider: Eine Instanz des konfigurierten AI-Providers
        """
        provider_name = AI_PROVIDER.lower()
        
        if provider_name == 'openai':
            logger.info("Verwende OpenAI für die Analyse")
            return OpenAIProvider()
        elif provider_name == 'anthropic':
            logger.info("Verwende Anthropic Claude für die Analyse")
            return AnthropicProvider()
        elif provider_name == 'custom':
            logger.info("Verwende Custom API für die Analyse")
            return CustomProvider()
        else:
            logger.error(f"KI-Anbieter '{provider_name}' nicht unterstützt")
            raise ValueError(f"KI-Anbieter '{provider_name}' nicht unterstützt")
