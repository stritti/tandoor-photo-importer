"""
Konfigurationsdatei für KI-Prompts

Diese Datei enthält vordefinierte Prompts für verschiedene Anwendungsfälle.
"""

# Standard-Prompt für allgemeine Bildanalyse
DEFAULT_PROMPT = "Was ist auf diesem Bild zu sehen? Beschreibe das Bild detailliert."

# Spezifische Prompts für verschiedene Anwendungsfälle
PROMPTS = {
    # Allgemeine Bildanalyse
    "general": DEFAULT_PROMPT,
    
    # Lebensmittel-Erkennung
    "food": "Welche Lebensmittel sind auf diesem Bild zu sehen? Liste alle erkennbaren Zutaten auf.",
    
    # Rezept-Analyse
    "recipe": "Handelt es sich um ein Gericht? Wenn ja, welches Gericht ist auf dem Bild zu sehen? Beschreibe die Zutaten und gib wenn möglich ein einfaches Rezept dafür an.",
    
    # Nährwertanalyse
    "nutrition": "Welche Lebensmittel sind auf diesem Bild zu sehen? Schätze die ungefähren Nährwerte (Kalorien, Protein, Kohlenhydrate, Fett) für die sichtbaren Portionen.",
}

def get_prompt(prompt_type="general"):
    """
    Gibt einen vordefinierten Prompt basierend auf dem angegebenen Typ zurück.
    
    Args:
        prompt_type: Typ des Prompts (z.B. "general", "food", "recipe")
        
    Returns:
        str: Der vordefinierte Prompt
    """
    return PROMPTS.get(prompt_type.lower(), DEFAULT_PROMPT)
