# FitnessAI Renovation Design

**Date:** 2026-05-21
**Status:** Approved

## Overview

Renovate the FitnessAI project from a monolithic Gradio app into a well-structured food calorie management system with proper frontend/backend separation, Supabase database, and modern AI model integration.

## Architecture

```
FitnessAI/
├── app_main.py              # Gradio entry — UI assembly and event binding only
├── config.py                # Unified config from .env
├── services/
│   ├── __init__.py
│   ├── supabase_client.py   # Supabase connection, query, write
│   ├── food_recognition.py  # Qwen 3.6 Plus food detection
│   └── ai_advisor.py        # DeepSeek V4 Pro diet/exercise advice
├── ui/
│   ├── __init__.py
│   ├── components.py        # Reusable UI components (stat cards, charts)
│   └── dashboard.py         # Dashboard layout
├── utils/
│   ├── __init__.py
│   ├── health_calc.py       # BMI/BMR/calorie target calculations
│   └── formatters.py        # Data formatting helpers
├── prompts/
│   ├── food_detection.txt   # Food recognition system prompt
│   └── diet_advice.txt      # Diet advice prompt
├── .env.example             # Environment variable template
├── .gitignore               # Ignores .env, __pycache__, etc.
├── requirements.txt
└── README.md
```

**Principle:** `app_main.py` does UI assembly only. `services/` handles all external calls. `ui/` contains reusable Gradio components. All keys read from `.env`.

## Data Flow

```
User uploads food image → Qwen 3.6 Plus recognition → returns food name + weight
→ Query Supabase food_library for kcal/100g → calculate total kcal
→ Write to Supabase meal_records → Dashboard updates charts in real-time
```

## Database (Supabase)

### `food_library` — food calorie reference

| Column | Type | Description |
|--------|------|-------------|
| id | int8 (PK) | auto-increment |
| name | text | food name |
| kcal_per_100g | float4 | kcal per 100g |
| category | text | staple/meat/vegetable/drink/snack |
| created_at | timestamptz | timestamp |

### `meal_records` — user meal records

| Column | Type | Description |
|--------|------|-------------|
| id | int8 (PK) | auto-increment |
| food_name | text | food name |
| weight_grams | int4 | weight in grams |
| kcal | float4 | calculated calories |
| meal_type | text | breakfast/lunch/dinner/snack |
| image_url | text | optional Supabase Storage URL |
| recorded_at | timestamptz | record time |

### `user_profiles` — user body profile

| Column | Type | Description |
|--------|------|-------------|
| id | uuid (PK) | user ID |
| gender | text | gender |
| age | int4 | age |
| height_cm | float4 | height |
| weight_kg | float4 | current weight |
| target_weight_kg | float4 | target weight |
| goal | text | lose/gain/maintain |
| updated_at | timestamptz | last update |

## UI Layout (Dashboard-style)

**5 functional areas, top to bottom:**

1. **4 stat cards** — BMI, BMR, target calories, today's intake (key metrics at a glance)
2. **Food recognition** — image upload + meal type selector + recognition results side by side
3. **7-day calorie trend bar chart** — daily intake visualization, green=within target, red=over
4. **AI health advice** — buttons for diet advice / exercise guidance + result display
5. **Today's meal records table** — time, food, weight, calories

**Interaction flow:** Set profile → Photo recognition → View dashboard → Get AI advice

## AI Model Integration

| Task | Model | API |
|------|-------|-----|
| Food image recognition | Qwen 3.6 Plus (qwen-vl-plus) | DashScope |
| Diet advice | DeepSeek V4 Pro | DeepSeek API |
| Exercise guidance | DeepSeek V4 Pro | DeepSeek API |

## Security

- All API keys in `.env`, excluded via `.gitignore`
- `.env.example` provides template with placeholder values
- No hardcoded paths — use `os.path`/`pathlib` for cross-platform compatibility

## Migration from Old Version

| Old | New |
|-----|-----|
| SQLite `app_data.db` | Supabase `food_library` + `meal_records` |
| GPT-4o-mini food recognition | Qwen 3.6 Plus |
| Qwen-VL-Plus for advice | DeepSeek V4 Pro |
| Hardcoded API keys | `.env` config |
| Windows-only paths | `pathlib` cross-platform |
| Monolithic `app_main.py` | Separated `services/` + `ui/` + `utils/` |
| Text-only output | Charts + stat cards + tables |
| No meal type | breakfast/lunch/dinner/snack |
| No user profile | `user_profiles` table |
