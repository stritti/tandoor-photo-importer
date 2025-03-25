import os
import base64
from decouple import config
import requests
from openai import OpenAI

# Konfiguration aus Umgebungsvariablen
AI_PROVIDER = config('AI_PROVIDER', default='openai')
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4-vision-preview')
MAX_TOKENS = config('MAX_TOKENS', default=300, cast=int)

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
        provider = AI_PROVIDER.lower()
        
        if provider == 'openai':
            return AIService._analyze_with_openai(image_path, prompt)
        elif provider == 'custom':
            return AIService._analyze_with_custom_api(image_path, prompt)
        else:
            return {
                "provider": "none",
                "error": f"KI-Anbieter '{provider}' nicht unterstützt oder konfiguriert"
            }
    
    @staticmethod
    def _analyze_with_openai(image_path, prompt):
        """Analysiert ein Bild mit OpenAI Vision API"""
        if not OPENAI_API_KEY:
            return {
                "provider": "openai",
                "error": "OpenAI API-Schlüssel nicht konfiguriert"
            }
        
        try:
            # Bild in base64 konvertieren
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Initialisiere den OpenAI-Client nur mit dem API-Key
            # Die neuere Version der OpenAI-Bibliothek unterstützt 'proxies' nicht mehr als direktes Argument
            client = OpenAI(api_key=OPENAI_API_KEY)
            
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
            
            return {
                "provider": "openai",
                "response": response.choices[0].message.content,
                "model": OPENAI_MODEL
            }
            
        except Exception as e:
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
            return {
                "provider": "custom",
                "error": "Benutzerdefinierte API nicht konfiguriert"
            }
        
        try:
            with open(image_path, "rb") as image_file:
                files = {"image": image_file}
                data = {"prompt": prompt}
                headers = {"Authorization": f"Bearer {CUSTOM_API_KEY}"}
                
                response = requests.post(
                    CUSTOM_API_URL,
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    return {
                        "provider": "custom",
                        "response": response.json()
                    }
                else:
                    return {
                        "provider": "custom",
                        "error": f"API-Fehler: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {
                "provider": "custom",
                "error": str(e)
            }
