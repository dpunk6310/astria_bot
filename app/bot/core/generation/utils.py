import json
import random


def get_random_prompt(json_file: str, gender: str, category_slug: str) -> str:
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if gender not in data:
            raise ValueError("Invalid gender. Choose 'man' or 'woman'.")
        
        categories = data[gender]["categories"]
        
        for category in categories:
            if category["slug"] == category_slug:
                return random.choice(category["promts"])
        
        raise ValueError("Category not found.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error loading JSON file: {e}"
      
      
def get_categories(json_file: str, gender: str) -> str:
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if gender not in data:
            raise ValueError("Invalid gender. Choose 'man' or 'woman'.")
        
        categories = []
        categories_json = data[gender]["categories"]
        for i in categories_json:
          categories.append({"name": i.get("name"), "slug": i.get("slug")})
        
        return categories
        
    except (FileNotFoundError, json.JSONDecodeError) as err:
        raise err