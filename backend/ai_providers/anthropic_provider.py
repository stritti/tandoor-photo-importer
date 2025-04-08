import base64
import logging
import traceback
import os
from io import BytesIO
from PIL import Image
from decouple import config
import anthropic

from base_provider import BaseAIProvider

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
            
            # Bild komprimieren und in base64 konvertieren
            base64_image, media_type = self._compress_and_encode_image(image_path)
            
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
        
    def _compress_and_encode_image(self, image_path, max_size_mb=4.5, quality_start=85):
        """
        Komprimiert ein Bild und konvertiert es in base64
        
        Args:
            image_path: Pfad zur Bilddatei
            max_size_mb: Maximale Größe in MB
            quality_start: Anfängliche JPEG-Qualität
            
        Returns:
            tuple: (base64-kodiertes Bild, Medientyp)
        """
        # Medientyp bestimmen
        original_media_type = self._determine_media_type(image_path)
        
        # Bild öffnen
        img = Image.open(image_path)
        
        # Konvertieren zu RGB, falls es sich um RGBA handelt (für JPEG-Konvertierung)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Maximale Größe in Bytes
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Ausgabeformat bestimmen (immer JPEG für Kompression)
        output_format = "JPEG"
        media_type = "image/jpeg"
        
        # Komprimierungsschleife
        quality = quality_start
        img_io = BytesIO()
        img.save(img_io, format=output_format, quality=quality)
        
        # Wenn das Bild bereits klein genug ist, verwenden wir es direkt
        if img_io.tell() <= max_size_bytes:
            img_io.seek(0)
            return base64.b64encode(img_io.read()).decode('utf-8'), media_type
        
        # Sonst reduzieren wir die Qualität schrittweise
        while quality > 10 and img_io.tell() > max_size_bytes:
            quality -= 10
            img_io = BytesIO()
            img.save(img_io, format=output_format, quality=quality)
        
        # Wenn die Qualitätsreduktion nicht ausreicht, verkleinern wir das Bild
        if img_io.tell() > max_size_bytes:
            # Originalgröße
            width, height = img.size
            
            # Skalierungsfaktor berechnen
            scale_factor = 0.9  # Reduziere um 10% in jeder Iteration
            
            while img_io.tell() > max_size_bytes and scale_factor > 0.1:
                # Neue Größe berechnen
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                # Bild verkleinern
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Speichern und Größe prüfen
                img_io = BytesIO()
                resized_img.save(img_io, format=output_format, quality=quality)
                
                # Wenn immer noch zu groß, weiter verkleinern
                if img_io.tell() > max_size_bytes:
                    scale_factor *= 0.9
                else:
                    break
        
        # Zurücksetzen des Positionszeigers und Rückgabe des komprimierten Bildes
        img_io.seek(0)
        logger.info(f"Bild komprimiert: Originalgröße unbekannt -> {img_io.tell()/1024/1024:.2f} MB (Qualität: {quality})")
        
        return base64.b64encode(img_io.read()).decode('utf-8'), media_type
