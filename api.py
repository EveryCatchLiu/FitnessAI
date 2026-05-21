"""FitnessAI API — FastAPI backend exposing services as REST endpoints."""
import json
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from services.supabase_client import (
    search_food_kcal, insert_meal_record, get_meal_records,
    get_daily_summary, get_today_total_kcal, upsert_user_profile, get_user_profile
)
from services.food_recognition import recognize_food, review_food_data
from services.ai_advisor import get_diet_advice, get_exercise_advice
from utils.health_calc import calc_bmi, calc_bmr, calc_target_calories, calc_goal_from_weights

app = FastAPI(title="FitnessAI API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


# ---- Static files ----

@app.get("/")
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


# ---- Profile ----

@app.get("/api/profile")
async def api_get_profile():
    profile = get_user_profile()
    if profile:
        return {
            "gender": profile["gender"], "age": profile["age"],
            "height_cm": profile["height_cm"], "weight_kg": profile["weight_kg"],
            "target_weight_kg": profile["target_weight_kg"], "goal": profile["goal"]
        }
    return None


@app.post("/api/profile")
async def api_save_profile(data: dict):
    goal = calc_goal_from_weights(data["weight_kg"], data["target_weight_kg"])
    upsert_user_profile(
        data["gender"], data["age"], data["height_cm"],
        data["weight_kg"], data["target_weight_kg"], goal
    )
    return {"status": "ok", "goal": goal}


# ---- Stats ----

@app.get("/api/stats")
async def api_get_stats():
    profile = get_user_profile()
    if profile:
        bmi = calc_bmi(profile["height_cm"], profile["weight_kg"])
        bmr = calc_bmr(profile["gender"], profile["age"], profile["height_cm"], profile["weight_kg"])
        target = calc_target_calories(profile["gender"], profile["age"], profile["height_cm"], profile["weight_kg"], profile["goal"])
    else:
        bmi, bmr, target = 0, 0, 2000

    today_kcal = get_today_total_kcal()

    return {
        "bmi": bmi, "bmr": bmr, "target_kcal": target, "today_kcal": today_kcal
    }


# ---- Daily summary / chart data ----

@app.get("/api/daily-summary")
async def api_daily_summary(days: int = 7):
    return get_daily_summary(days)


# ---- Food recognition ----

@app.post("/api/recognize-food")
async def api_recognize_food(image: UploadFile = File(...)):
    # Save uploaded file temporarily
    tmp_path = STATIC_DIR / "uploads" / image.filename
    tmp_path.parent.mkdir(exist_ok=True)
    content = await image.read()
    tmp_path.write_bytes(content)

    try:
        raw = recognize_food(str(tmp_path))
        reviewed = review_food_data(raw)

        for item in reviewed:
            name = item.get("name", "")
            model_kcal = item.get("kcal", 0)
            # If model didn't provide kcal, try database lookup
            if not model_kcal or model_kcal == 0:
                kcal_per_100g = search_food_kcal(name)
                weight = item.get("weight", 0)
                if kcal_per_100g:
                    item["kcal"] = round(weight * 0.01 * kcal_per_100g, 1)
            # If model provided kcal, use it directly (trust AI nutrition knowledge)
            else:
                item["kcal"] = model_kcal

        total = round(sum(item.get("kcal", 0) for item in reviewed), 1)
        return {"items": reviewed, "total_kcal": total}
    except Exception as e:
        return JSONResponse({"error": str(e), "items": [], "total_kcal": 0}, status_code=500)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ---- Meal records ----

@app.post("/api/meals")
async def api_save_meals(data: dict):
    records = data.get("records", [])
    meal_type = data.get("meal_type", "lunch")
    for item in records:
        insert_meal_record(
            food_name=item.get("name", "?"),
            weight_grams=int(item.get("weight", 0)),
            kcal=float(item.get("kcal", 0)),
            meal_type=meal_type,
        )
    return {"status": "ok", "saved": len(records)}


@app.get("/api/meals")
async def api_get_meals(days: int = 7):
    return get_meal_records(days)


# ---- AI Advice ----

@app.get("/api/advice/diet")
async def api_diet_advice():
    return {"advice": get_diet_advice()}


@app.get("/api/advice/exercise")
async def api_exercise_advice():
    return {"advice": get_exercise_advice()}


# ----

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7862)
