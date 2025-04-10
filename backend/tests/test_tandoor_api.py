import pytest
from unittest.mock import patch, MagicMock
import json
# Path is now set in conftest.py
# Import from backend package
from tandoor_api import (
    prepare_recipe_data,
    extract_food_name,
    extract_amount,
    extract_unit,
    extract_note
)

def test_prepare_recipe_data_minimal():
    """Test prepare_recipe_data with minimal input."""
    recipe_json_ld = {
        "name": "Simple Recipe",
        "@type": "Recipe"
    }
    
    result = prepare_recipe_data(recipe_json_ld)
    
    assert result["name"] == "Simple Recipe"
    assert result["description"] == ""
    assert result["servings"] == 4  # Default value
    assert result["working_time"] == 0
    assert result["waiting_time"] == 0
    assert result["keywords"] == []

def test_prepare_recipe_data_complete():
    """Test prepare_recipe_data with complete input."""
    recipe_json_ld = {
        "@context": "https://schema.org/",
        "@type": "Recipe",
        "name": "Chocolate Cake",
        "description": "Delicious chocolate cake",
        "recipeYield": 8,
        "prepTime": "PT30M",
        "cookTime": "PT1H",
        "keywords": "chocolate,cake,dessert",
        "recipeIngredient": [
            "200g flour",
            "100g sugar",
            "50g butter"
        ],
        "recipeInstructions": [
            "Mix dry ingredients",
            "Add wet ingredients",
            "Bake at 180°C"
        ]
    }
    
    result = prepare_recipe_data(recipe_json_ld)
    
    assert result["name"] == "Chocolate Cake"
    assert result["description"] == "Delicious chocolate cake"
    assert result["servings"] == 8
    assert result["working_time"] == 30
    assert result["waiting_time"] == 60
    assert len(result["keywords"]) == 3
    assert result["keywords"][0]["name"] == "chocolate"
    assert len(result["steps"]) == 3
    assert result["steps"][0]["instruction"] == "Mix dry ingredients"
    assert len(result["steps"][0]["ingredients"]) == 3

def test_prepare_recipe_data_string_instructions():
    """Test prepare_recipe_data with string instructions."""
    recipe_json_ld = {
        "name": "Simple Recipe",
        "recipeInstructions": "Mix all ingredients and bake.",
        "recipeIngredient": ["100g flour"]
    }
    
    result = prepare_recipe_data(recipe_json_ld)
    
    assert result["steps"][0]["instruction"] == "Mix all ingredients and bake."
    assert len(result["steps"][0]["ingredients"]) == 1

def test_extract_food_name():
    """Test extract_food_name function."""
    assert extract_food_name("200g flour") == "g flour"
    assert extract_food_name("1 apple") == "apple"
    assert extract_food_name("salt") == "salt"

def test_extract_amount():
    """Test extract_amount function."""
    assert extract_amount("200g flour") == 200.0
    assert extract_amount("1.5 cups sugar") == 1.5
    assert extract_amount("a pinch of salt") == 0

def test_extract_unit():
    """Test extract_unit function."""
    assert extract_unit("200g flour") == "g"
    assert extract_unit("1 TL salt") == "TL"
    assert extract_unit("2 Stück Äpfel") == "Stück"
    assert extract_unit("some salt") == ""

def test_extract_note():
    """Test extract_note function."""
    assert extract_note("flour (sifted)") == "sifted"
    assert extract_note("sugar (brown, not white)") == "brown, not white"
    assert extract_note("plain flour") == ""
