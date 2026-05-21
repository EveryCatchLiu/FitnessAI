"""Supabase client — query, insert, upsert operations."""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _client


def search_food_kcal(name: str) -> float | None:
    """Search food_library by name, return kcal_per_100g or None."""
    client = get_client()
    result = client.table("food_library").select("kcal_per_100g").ilike("name", f"%{name}%").limit(1).execute()
    if result.data:
        return result.data[0]["kcal_per_100g"]
    # Try without first char (handles LLM adding prefixes)
    if len(name) > 1:
        result = client.table("food_library").select("kcal_per_100g").ilike("name", f"%{name[1:]}%").limit(1).execute()
        if result.data:
            return result.data[0]["kcal_per_100g"]
    return None


def insert_meal_record(food_name: str, weight_grams: int, kcal: float, meal_type: str = "lunch", image_url: str = None) -> dict:
    """Insert a meal record, return the created row."""
    client = get_client()
    result = client.table("meal_records").insert({
        "food_name": food_name,
        "weight_grams": weight_grams,
        "kcal": round(kcal, 1),
        "meal_type": meal_type,
        "image_url": image_url,
    }).execute()
    return result.data[0] if result.data else {}


def get_meal_records(days: int = 7) -> list[dict]:
    """Get meal records from the last N days, ordered by most recent."""
    from datetime import datetime, timedelta

    client = get_client()
    since = (datetime.now() - timedelta(days=days)).isoformat()

    result = client.table("meal_records").select("*").gte("recorded_at", since).order("recorded_at", desc=True).execute()
    return result.data or []


def get_daily_summary(days: int = 7) -> list[dict]:
    """Get per-day calorie totals for the last N days."""
    from datetime import datetime, timedelta
    from collections import defaultdict

    records = get_meal_records(days)
    daily: dict[str, float] = defaultdict(float)
    for r in records:
        date_str = r["recorded_at"][:10] if r.get("recorded_at") else ""
        daily[date_str] += r.get("kcal", 0)

    result = []
    for i in range(days - 1, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        result.append({"date": date, "total_kcal": round(daily.get(date, 0), 1)})
    return result


def get_today_total_kcal() -> float:
    """Get total kcal consumed today."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    client = get_client()
    result = client.table("meal_records").select("kcal").gte("recorded_at", today).execute()
    return round(sum(r["kcal"] for r in (result.data or [])), 1)


def upsert_user_profile(gender: str, age: int, height_cm: float, weight_kg: float, target_weight_kg: float, goal: str) -> dict:
    """Upsert the single user profile. Uses a fixed ID for single-user simplicity."""
    client = get_client()
    result = client.table("user_profiles").upsert({
        "id": "00000000-0000-0000-0000-000000000001",
        "gender": gender,
        "age": age,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "target_weight_kg": target_weight_kg,
        "goal": goal,
        "updated_at": "now()",
    }).execute()
    return result.data[0] if result.data else {}


def get_user_profile() -> dict | None:
    """Get the single user profile."""
    client = get_client()
    result = client.table("user_profiles").select("*").limit(1).execute()
    return result.data[0] if result.data else None
