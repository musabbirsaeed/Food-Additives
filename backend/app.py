import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

app = FastAPI(title="Food Nutrition API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NUTRIENT_MAP = {
    "Energy": "calories_kcal",
    "Energy (Atwater General Factors)": "calories_kcal",
    "Energy (Atwater Specific Factors)": "calories_kcal",
    "Protein": "protein_g",
    "Total lipid (fat)": "fat_g",
    "Carbohydrate, by difference": "carbs_g",
    "Fiber, total dietary": "fiber_g",
    "Sugars, total including NLEA": "sugars_g",
    "Sodium, Na": "sodium_mg",
    "Potassium, K": "potassium_mg",
    "Calcium, Ca": "calcium_mg",
    "Iron, Fe": "iron_mg",
    "Magnesium, Mg": "magnesium_mg",
    "Phosphorus, P": "phosphorus_mg",
    "Zinc, Zn": "zinc_mg",
    "Vitamin C, total ascorbic acid": "vitamin_c_mg",
    "Vitamin A, RAE": "vitamin_a_ug",
    "Vitamin D (D2 + D3)": "vitamin_d_ug",
    "Vitamin E (alpha-tocopherol)": "vitamin_e_mg",
    "Vitamin K (phylloquinone)": "vitamin_k_ug",
    "Thiamin": "vitamin_b1_mg",
    "Riboflavin": "vitamin_b2_mg",
    "Niacin": "vitamin_b3_mg",
    "Vitamin B-6": "vitamin_b6_mg",
    "Folate, total": "folate_ug",
    "Vitamin B-12": "vitamin_b12_ug",
}


def to_number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def extract_nutrients(food_nutrients: List[Dict[str, Any]]) -> Dict[str, float]:
    result: Dict[str, float] = {}
    for item in food_nutrients:
        nutrient_name = item.get("nutrientName")
        value = item.get("value")
        if nutrient_name in NUTRIENT_MAP and value is not None:
            result[NUTRIENT_MAP[nutrient_name]] = to_number(value)
    return result


def build_response(food_item: Dict[str, Any]) -> Dict[str, Any]:
    nutrients = extract_nutrients(food_item.get("foodNutrients", []))
    return {
        "food": food_item.get("description"),
        "brand": food_item.get("brandOwner"),
        "fdc_id": food_item.get("fdcId"),
        "serving_size": food_item.get("servingSize"),
        "serving_size_unit": food_item.get("servingSizeUnit"),
        "calories_kcal": nutrients.get("calories_kcal", 0.0),
        "macros_g": {
            "protein": nutrients.get("protein_g", 0.0),
            "carbs": nutrients.get("carbs_g", 0.0),
            "fat": nutrients.get("fat_g", 0.0),
            "fiber": nutrients.get("fiber_g", 0.0),
            "sugars": nutrients.get("sugars_g", 0.0),
        },
        "micros": {
            "sodium_mg": nutrients.get("sodium_mg", 0.0),
            "potassium_mg": nutrients.get("potassium_mg", 0.0),
            "calcium_mg": nutrients.get("calcium_mg", 0.0),
            "iron_mg": nutrients.get("iron_mg", 0.0),
            "magnesium_mg": nutrients.get("magnesium_mg", 0.0),
            "phosphorus_mg": nutrients.get("phosphorus_mg", 0.0),
            "zinc_mg": nutrients.get("zinc_mg", 0.0),
            "vitamin_c_mg": nutrients.get("vitamin_c_mg", 0.0),
            "vitamin_a_ug": nutrients.get("vitamin_a_ug", 0.0),
            "vitamin_d_ug": nutrients.get("vitamin_d_ug", 0.0),
            "vitamin_e_mg": nutrients.get("vitamin_e_mg", 0.0),
            "vitamin_k_ug": nutrients.get("vitamin_k_ug", 0.0),
            "vitamin_b1_mg": nutrients.get("vitamin_b1_mg", 0.0),
            "vitamin_b2_mg": nutrients.get("vitamin_b2_mg", 0.0),
            "vitamin_b3_mg": nutrients.get("vitamin_b3_mg", 0.0),
            "vitamin_b6_mg": nutrients.get("vitamin_b6_mg", 0.0),
            "folate_ug": nutrients.get("folate_ug", 0.0),
            "vitamin_b12_ug": nutrients.get("vitamin_b12_ug", 0.0),
        },
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/nutrition")
def get_nutrition(
    food: str = Query(..., min_length=2, description="Food name, e.g. banana"),
    page_size: int = Query(5, ge=1, le=25),
) -> Dict[str, Any]:
    if not USDA_API_KEY:
        raise HTTPException(status_code=500, detail="USDA_API_KEY is missing in environment")

    params = {"api_key": USDA_API_KEY, "query": food, "pageSize": page_size}

    try:
        response = requests.get(USDA_SEARCH_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"USDA API request failed: {exc}") from exc

    foods = data.get("foods", [])
    if not foods:
        raise HTTPException(status_code=404, detail=f"No food found for '{food}'")

    normalized = [build_response(item) for item in foods]
    return {"query": food, "count": len(normalized), "results": normalized}
