"""
Tandoor API Integration

Dieses Modul stellt Funktionen zur Interaktion mit der Tandoor-API bereit.
"""

import json
import logging
import requests
from decouple import config

# Konfiguration aus Umgebungsvariablen
TANDOOR_API_URL = config('TANDOOR_API_URL', default='')

# Logger
logger = logging.getLogger('tandoor_api')

def get_auth_token(username, password):
    """
    Holt ein Authentifizierungstoken von der Tandoor API
    
    Args:
        username: Benutzername für Tandoor
        password: Passwort für Tandoor
        
    Returns:
        str: Das Authentifizierungstoken oder None bei Fehler
    """
    if not TANDOOR_API_URL:
        logger.error("Tandoor API URL nicht konfiguriert")
        return None
    
    try:
        logger.info(f"Fordere Auth-Token von {TANDOOR_API_URL}/api-token-auth/ an")
        response = requests.post(
            f"{TANDOOR_API_URL}/api-token-auth/",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            token = response.json().get("token")
            logger.info("Auth-Token erfolgreich erhalten")
            return token
        else:
            logger.error(f"Fehler beim Abrufen des Auth-Tokens: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Auth-Tokens: {str(e)}")
        return None

def import_recipe(recipe_data, auth_token):
    """
    Importiert ein Rezept in Tandoor über die API
    
    Args:
        recipe_data: JSON-LD Daten des Rezepts
        auth_token: Authentifizierungstoken für die API
        
    Returns:
        dict: Ergebnis des Imports
    """
    if not TANDOOR_API_URL:
        logger.error("Tandoor API URL nicht konfiguriert")
        return {
            "success": False,
            "error": "Tandoor API URL nicht konfiguriert"
        }
    
    if not auth_token:
        logger.error("Kein Auth-Token angegeben")
        return {
            "success": False,
            "error": "Kein Auth-Token angegeben"
        }
    
    try:
        logger.info("Starte Rezept-Import in Tandoor")
        
        # Parse recipe_data if it's a string
        if isinstance(recipe_data, str):
            recipe_data = json.loads(recipe_data)

        logger.info(f"Rezeptdaten: {recipe_data}")

        # Prepare the data for import
        #TODO import_data = prepare_recipe_data(recipe_data)
        import_data = recipe_data
        logger.info(f"Vorbereitete Rezeptdaten: {import_data}")
        
        # Sende Anfrage an Tandoor API
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "data": json.dumps(import_data),
            "url": ""
        }

        logger.debug(f"Importiere Rezept in Tandoor: {data}")
        
        logger.info(f"Sende Anfrage an Tandoor API: {TANDOOR_API_URL}/api/recipe-from-source/")
        response = requests.post(
            f"{TANDOOR_API_URL}/api/recipe-from-source/",
            json=data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            logger.info("Rezept erfolgreich in Tandoor importiert")
            return {
                "success": True,
                "recipe_id": response.json().get("id"),
                "recipe_url": f"{TANDOOR_API_URL}/recipe/{response.json().get('id')}"
            }
        else:
            logger.error(f"Fehler beim Import: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"API-Fehler: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        logger.error(f"Fehler beim Rezept-Import: {str(e)}")
        logger.exception("Fehler beim Rezept-Import", exc_info=True, stack_info=True, extra={"recipe_data": recipe_data})
        return {
            "success": False,
            "error": str(e)
        }

def prepare_recipe_data(recipe_json_ld):
    """
    Bereitet die JSON-LD Daten für den Import in Tandoor vor
    
    Args:
        recipe_json_ld: JSON-LD Daten des Rezepts
        
    Returns:
        dict: Für Tandoor formatierte Daten
    """
    try:
        recipe_data = recipe_json_ld
            
        # Extrahiere die relevanten Daten aus dem JSON-LD Format
        tandoor_data = {
            "name": recipe_data.get("name", "Unbenanntes Rezept"),
            "description": recipe_data.get("description", ""),
            "servings": recipe_data.get("recipeYield", 4),
            "working_time": convert_time_to_minutes(recipe_data.get("prepTime", "PT0M")),
            "waiting_time": convert_time_to_minutes(recipe_data.get("cookTime", "PT0M")),
            "keywords": [{"name": kw} for kw in recipe_data.get("keywords", "").split(",") if kw.strip()],
        }
        
        # Zutaten verarbeiten
        if "recipeIngredient" in recipe_data:
            ingredients = []
            for ingredient in recipe_data["recipeIngredient"]:
                ingredients.append({
                    "food": {"name": extract_food_name(ingredient)},
                    "amount": extract_amount(ingredient),
                    "unit": {"name": extract_unit(ingredient)},
                    "note": extract_note(ingredient)
                })
            tandoor_data["steps"] = [{"ingredients": ingredients, "instruction": ""}]
        
        # Anweisungen verarbeiten
        if "recipeInstructions" in recipe_data:
            instructions = recipe_data["recipeInstructions"]
            if isinstance(instructions, list):
                # Wenn Anweisungen als Liste vorliegen
                for i, instruction in enumerate(instructions):
                    if i < len(tandoor_data.get("steps", [])):
                        # Add instruction to existing step
                        tandoor_data["steps"][i]["instruction"] = instruction if isinstance(instruction, str) else instruction.get("text", "")
                    else:
                        # Create new step
                        tandoor_data.setdefault("steps", []).append({
                            "instruction": instruction if isinstance(instruction, str) else instruction.get("text", ""),
                            "ingredients": []
                        })
            elif isinstance(instructions, str):
                # If instructions is a string
                if tandoor_data.get("steps"):
                    tandoor_data["steps"][0]["instruction"] = instructions
                else:
                    tandoor_data["steps"] = [{"instruction": instructions, "ingredients": []}]
        
        return tandoor_data
        
    except Exception as e:
        logger.error(f"Fehler bei der Datenvorbereitung: {str(e)}")
        raise

def convert_time_to_minutes(iso_duration):
    """
    Konvertiert ISO 8601 Zeitdauer in Minuten
    
    Args:
        iso_duration: ISO 8601 Zeitdauer (z.B. "PT1H30M")
        
    Returns:
        int: Dauer in Minuten
    """
    if not iso_duration or not isinstance(iso_duration, str):
        return 0
        
    minutes = 0
    
    # Entferne PT vom Anfang
    duration = iso_duration.replace("PT", "")
    
    # Stunden
    if "H" in duration:
        hours_part = duration.split("H")[0]
        if hours_part:
            minutes += int(hours_part) * 60
        duration = duration.split("H")[1]
    
    # Minuten
    if "M" in duration:
        minutes_part = duration.split("M")[0]
        if minutes_part:
            minutes += int(minutes_part)
    
    return minutes

def extract_food_name(ingredient_text):
    """Extrahiert den Lebensmittelnamen aus einem Zutatentext"""
    # Einfache Implementierung - in der Praxis würde man hier NLP verwenden
    parts = ingredient_text.split()
    if len(parts) >= 2:
        # Versuche, Menge und Einheit zu ignorieren
        return " ".join(parts[1:])
    return ingredient_text

def extract_amount(ingredient_text):
    """Extrahiert die Menge aus einem Zutatentext"""
    parts = ingredient_text.split()
    if parts and parts[0].replace('.', '', 1).isdigit():
        try:
            return float(parts[0])
        except ValueError:
            pass
    return 0

def extract_unit(ingredient_text):
    """Extrahiert die Einheit aus einem Zutatentext"""
    common_units = ["g", "kg", "ml", "l", "EL", "TL", "Stück", "Prise"]
    parts = ingredient_text.split()
    if len(parts) >= 2:
        for unit in common_units:
            if unit.lower() in parts[1].lower():
                return unit
    return ""

def extract_note(ingredient_text):
    """Extrahiert Notizen aus einem Zutatentext"""
    # Suche nach Klammern, die oft Notizen enthalten
    if "(" in ingredient_text and ")" in ingredient_text:
        start = ingredient_text.find("(")
        end = ingredient_text.find(")")
        if start < end:
            return ingredient_text[start+1:end]
    return ""
