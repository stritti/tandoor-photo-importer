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
    "recipe": "I have old cooking recipes on paper, which I want to digitalize and upload to my App Tandoor.\
        Tandoor could import recipes in JSON-LD best. For the correct format refer to https://developers.google.com/search/docs/appearance/structured-data/recipe and https://schema.org/Recipe \
        Please extract the receipe of the given file and summarize it in two formats: first readable for me and second in JSON-LD to be possible to import it to Tandoor.\
        If you are unsure and something is not readable, please let me know. Mark any unsure suggestions. It is important to get accurate digital version of receipe.\
        Respect always language of recipe and answer always in same language which you found in the source! Do not use the promt language. Always the Language of the image.\
        If you find any ingredients, please extract them and provide the amount and unit.\
        If you find any instructions, please extract them and provide the instruction.\
        If you find any keywords, please extract them and provide them.\
        If you find any servings, please extract them and provide them.\
        If you find any time, please extract them and provide them.\
        If you find any temperature, please extract them and provide them.\
        If there are times for preparation and cooking then verify them and sum them if neccessary. \
        Verify always the JSON-LD-Format and provide it in a code block. \
        If you find any missing information, please let me know. \
        Please also search the internet to see if you can still find the recipe online and reference it if necessary.",
        # If there is a photo of the receipe within the screenshot, then extract this and add it to your conversion otherwise ask if you should create a picture which shows the result of recipe.",
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
