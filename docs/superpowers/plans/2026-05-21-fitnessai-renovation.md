# FitnessAI Renovation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Renovate FitnessAI from a monolithic Gradio app into a well-structured food calorie management system with Supabase database, AI-powered food recognition, and an interactive dashboard UI.

**Architecture:** Gradio frontend with separated service layer. `services/` handles all external calls (Supabase, Qwen, DeepSeek). `ui/` contains reusable Gradio components. `utils/` has pure calculation helpers. `app_main.py` only does UI assembly and event binding. All config read from `.env`.

**Tech Stack:** Python 3.11+, Gradio 5.x, Supabase Python SDK, OpenAI SDK (for Qwen DashScope + DeepSeek), Matplotlib, python-dotenv

---

### Task 1: Project Scaffold & Environment Setup

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `requirements.txt`
- Create: `config.py`
- Create: `services/__init__.py`
- Create: `ui/__init__.py`
- Create: `prompts/` (directory)
- Move: `demo/images/` → `images/`
- Move: `demo/prompt/sys_prompt_m1.txt` → `prompts/food_detection.txt`
- Move: `demo/prompt/sys_prompt_m1_review.txt` → `prompts/food_review.txt`

- [ ] **Step 1: Create .gitignore**

```bash
cat > /Users/liuzihao/VibeCoding/FitnessAI/.gitignore << 'GITIGNORE'
.env
__pycache__/
*.pyc
.gradio/
.superpowers/
*.db
.DS_Store
GITIGNORE
```

- [ ] **Step 2: Create .env.example**

```bash
cat > /Users/liuzihao/VibeCoding/FitnessAI/.env.example << 'ENVEXAMPLE'
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# DashScope (Qwen VL for food recognition)
DASHSCOPE_API_KEY=your-dashscope-api-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# DeepSeek (for diet/exercise advice)
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
ENVEXAMPLE
```

- [ ] **Step 3: Create requirements.txt**

```bash
cat > /Users/liuzihao/VibeCoding/FitnessAI/requirements.txt << 'REQS'
gradio>=5.0
openai>=1.50
supabase>=2.0
python-dotenv>=1.0
matplotlib>=3.8
REQS
```

- [ ] **Step 4: Create config.py**

```python
# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
```

- [ ] **Step 5: Create package __init__ files**

```bash
touch /Users/liuzihao/VibeCoding/FitnessAI/services/__init__.py
touch /Users/liuzihao/VibeCoding/FitnessAI/ui/__init__.py
```

- [ ] **Step 6: Create prompts/ directory and copy prompt files**

```bash
mkdir -p /Users/liuzihao/VibeCoding/FitnessAI/prompts
cp /Users/liuzihao/VibeCoding/FitnessAI/demo/prompt/sys_prompt_m1.txt /Users/liuzihao/VibeCoding/FitnessAI/prompts/food_detection.txt
cp /Users/liuzihao/VibeCoding/FitnessAI/demo/prompt/sys_prompt_m1_review.txt /Users/liuzihao/VibeCoding/FitnessAI/prompts/food_review.txt
```

- [ ] **Step 7: Move images to root level**

```bash
cp -r /Users/liuzihao/VibeCoding/FitnessAI/demo/images /Users/liuzihao/VibeCoding/FitnessAI/images
```

- [ ] **Step 8: Verify structure**

```bash
ls -la /Users/liuzihao/VibeCoding/FitnessAI/
# Should show: .gitignore, .env.example, requirements.txt, config.py, services/, ui/, prompts/, images/
```

---

### Task 2: Supabase Database Migration

**Files:**
- Create: `supabase_migration.sql`

- [ ] **Step 1: Create Supabase migration SQL**

```sql
-- supabase_migration.sql
-- Run this in Supabase SQL Editor to create the tables

CREATE TABLE IF NOT EXISTS food_library (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    kcal_per_100g REAL NOT NULL,
    category TEXT DEFAULT 'other',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meal_records (
    id BIGSERIAL PRIMARY KEY,
    food_name TEXT NOT NULL,
    weight_grams INTEGER NOT NULL,
    kcal REAL NOT NULL,
    meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')) DEFAULT 'lunch',
    image_url TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gender TEXT DEFAULT 'male',
    age INTEGER DEFAULT 25,
    height_cm REAL DEFAULT 170,
    weight_kg REAL DEFAULT 70,
    target_weight_kg REAL DEFAULT 70,
    goal TEXT DEFAULT 'maintain',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed common foods
INSERT INTO food_library (name, kcal_per_100g, category) VALUES
    ('米饭', 116, 'staple'),
    ('馒头', 223, 'staple'),
    ('面条', 137, 'staple'),
    ('全麦面包', 247, 'staple'),
    ('燕麦', 367, 'staple'),
    ('红薯', 86, 'staple'),
    ('鸡胸肉', 133, 'meat'),
    ('鸡腿', 181, 'meat'),
    ('猪肉', 242, 'meat'),
    ('牛肉', 125, 'meat'),
    ('羊肉', 203, 'meat'),
    ('三文鱼', 208, 'meat'),
    ('虾仁', 99, 'meat'),
    ('鸡蛋', 144, 'meat'),
    ('西兰花', 34, 'vegetable'),
    ('菠菜', 23, 'vegetable'),
    ('番茄', 18, 'vegetable'),
    ('黄瓜', 15, 'vegetable'),
    ('胡萝卜', 37, 'vegetable'),
    ('生菜', 15, 'vegetable'),
    ('苹果', 52, 'fruit'),
    ('香蕉', 89, 'fruit'),
    ('橙子', 47, 'fruit'),
    ('葡萄', 67, 'fruit'),
    ('草莓', 32, 'fruit'),
    ('牛奶', 64, 'drink'),
    ('豆浆', 31, 'drink'),
    ('可乐', 42, 'drink'),
    ('橙汁', 45, 'drink'),
    ('纯净水', 0, 'drink'),
    ('薯片', 536, 'snack'),
    ('巧克力', 546, 'snack'),
    ('坚果', 607, 'snack'),
    ('酸奶', 63, 'snack'),
    ('冰淇淋', 207, 'snack')
ON CONFLICT DO NOTHING;
```

- [ ] **Step 2: Note for user — run migration manually**

The user must open Supabase Dashboard → SQL Editor, paste the above SQL, and run it. This is a one-time manual step.

---

### Task 3: Supabase Client Service

**Files:**
- Create: `services/supabase_client.py`

- [ ] **Step 1: Write supabase_client.py**

```python
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
    """Get meal records from the last N days, grouped by date."""
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
    """Upsert the single user profile (id=1). Uses a fixed ID for single-user simplicity."""
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
```

---

### Task 4: Food Recognition Service

**Files:**
- Create: `services/food_recognition.py`

- [ ] **Step 1: Write food_recognition.py**

```python
"""Food image recognition via Qwen 3.6 Plus (DashScope)."""
import base64
import json
import re
from pathlib import Path

from openai import OpenAI

from config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, BASE_DIR

client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL)


def _load_prompt(name: str) -> str:
    path = BASE_DIR / "prompts" / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def recognize_food(image_path: str) -> list[dict]:
    """Analyze food image and return list of {name, weight, kcal} dicts."""
    prompt = _load_prompt("food_detection.txt")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
                ]
            }
        ]
    )

    content = response.choices[0].message.content
    return _extract_json(content)


def _extract_json(text: str) -> list[dict]:
    """Extract JSON list from markdown-wrapped or plain text."""
    match = re.search(r'\[\{.*?\}\]', text, re.DOTALL)
    if not match:
        match = re.search(r'```json\s*(\[\{.*?\}\])\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1) if match.lastindex else match.group(0))
        except json.JSONDecodeError:
            pass
    return []


def review_food_data(raw_data: list[dict]) -> list[dict]:
    """Second-pass review of food data for calorie sanity check."""
    from services.supabase_client import search_food_kcal

    prompt = _load_prompt("food_review.txt")

    response = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(raw_data, ensure_ascii=False)}
        ]
    )

    content = response.choices[0].message.content
    if not content:
        return raw_data

    # Try to extract corrected data
    try:
        match = re.search(r'\[\{.*?\}\]', content, re.DOTALL)
        if match:
            corrected = json.loads(match.group(0))
            # Merge calorie lookup
            for item in corrected:
                name = item.get("name", "")
                weight = item.get("weight", 0)
                kcal_per_100g = search_food_kcal(name)
                if kcal_per_100g:
                    item["kcal"] = round(weight * 0.01 * kcal_per_100g, 1)
                else:
                    item["kcal"] = item.get("kcal", 0)
            return corrected
    except (json.JSONDecodeError, SyntaxError):
        pass

    return raw_data
```

- [ ] **Step 2: Update prompts/food_detection.txt to remove hardcoded paths and ensure compatibility**

The existing prompt content is already good — it instructs the model to output JSON with food name, number, and weight. Just verify it has no hardcoded paths (it doesn't — it's just a system prompt).

---

### Task 5: AI Advisor Service

**Files:**
- Create: `services/ai_advisor.py`

- [ ] **Step 1: Write ai_advisor.py**

```python
"""AI-powered diet and exercise advice via DeepSeek V4 Pro."""
from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from services.supabase_client import get_meal_records, get_user_profile

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def get_diet_advice() -> str:
    """Generate personalized diet advice based on user profile and recent meals."""
    profile = get_user_profile()
    records = get_meal_records(7)

    if not profile:
        return "请先在仪表盘设置您的个人档案（性别、年龄、身高、体重、目标）。"

    user_info = f"性别: {profile['gender']}, 年龄: {profile['age']}, 身高: {profile['height_cm']}cm, 体重: {profile['weight_kg']}kg, 目标: {profile['goal']}到{profile['target_weight_kg']}kg"

    records_json = json.dumps(records, ensure_ascii=False, default=str)

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[{
            "role": "user",
            "content": (
                f"你是一个健康饮食指导师，请根据以下信息给出饮食建议。\n\n"
                f"用户信息: {user_info}\n"
                f"近7天饮食记录: {records_json}\n\n"
                f"要求: 1)饮食模式是否健康 2)三餐是否合理 3)目标预测 4)改进建议 限制300字以内。"
            )
        }]
    )
    return response.choices[0].message.content or "无法生成建议，请稍后重试。"


def get_exercise_advice() -> str:
    """Generate personalized exercise guidance."""
    profile = get_user_profile()
    records = get_meal_records(7)

    if not profile:
        return "请先在仪表盘设置您的个人档案。"

    user_info = f"性别: {profile['gender']}, 年龄: {profile['age']}, 身高: {profile['height_cm']}cm, 体重: {profile['weight_kg']}kg, 目标: {profile['goal']}到{profile['target_weight_kg']}kg"

    records_json = json.dumps(records, ensure_ascii=False, default=str)

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[{
            "role": "user",
            "content": (
                f"你是一个健康运动指导师，请根据以下信息给出运动建议。\n\n"
                f"用户信息: {user_info}\n"
                f"近7天饮食记录: {records_json}\n\n"
                f"要求: 提供至少两个运动类型，包含运动时间、强度，并在最后激励用户。限制300字以内。"
            )
        }]
    )
    return response.choices[0].message.content or "无法生成建议，请稍后重试。"
```

- [ ] **Step 2: Add missing import**

The `json` import is needed at the top of `ai_advisor.py`. Add `import json` after the openai import.

---

### Task 6: Health Calculation Utils

**Files:**
- Create: `utils/health_calc.py`

- [ ] **Step 1: Write health_calc.py**

```python
"""BMI, BMR, and calorie target calculations."""

def calc_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculate BMI. height in cm, weight in kg."""
    h_m = height_cm / 100
    return round(weight_kg / (h_m ** 2), 1)


def calc_bmr(gender: str, age: int, height_cm: float, weight_kg: float) -> float:
    """Calculate BMR using Mifflin-St Jeor equation."""
    if gender in ("男", "male"):
        return round(10 * weight_kg + 6.25 * height_cm - 5 * age + 5, 1)
    else:
        return round(10 * weight_kg + 6.25 * height_cm - 5 * age - 161, 1)


def calc_target_calories(gender: str, age: int, height_cm: float, weight_kg: float, goal: str) -> float:
    """Calculate daily calorie target based on goal."""
    bmr = calc_bmr(gender, age, height_cm, weight_kg)
    if goal in ("减重", "lose"):
        return round(bmr - 500, 1)
    elif goal in ("增重", "gain"):
        return round(bmr + 500, 1)
    return round(bmr, 1)


def calc_goal_from_weights(current_weight: float, target_weight: float) -> str:
    """Determine goal (减重/增重/保持) from weight comparison."""
    if target_weight < current_weight:
        return "减重"
    elif target_weight > current_weight:
        return "增重"
    return "保持"


def bmi_category(bmi: float) -> str:
    """Return BMI category in Chinese."""
    if bmi < 18.5:
        return "偏瘦"
    elif bmi < 24:
        return "正常范围"
    elif bmi < 28:
        return "偏重"
    else:
        return "肥胖"
```

---

### Task 7: UI Components

**Files:**
- Create: `ui/components.py`

- [ ] **Step 1: Write ui/components.py**

```python
"""Reusable Gradio UI components."""
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime

from services.supabase_client import get_daily_summary, get_today_total_kcal, get_meal_records


def make_stat_card_html(bmi: float, bmr: float, target_kcal: float) -> str:
    """Generate HTML for the 4 stat cards at the top of the dashboard."""
    cat = _bmi_category(bmi)
    today_kcal = get_today_total_kcal()
    remaining = round(target_kcal - today_kcal, 1)

    return f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px;margin-bottom:20px;">
        <div style="background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);text-align:center;">
            <div style="font-size:13px;color:#64748b;margin-bottom:6px;">BMI 指数</div>
            <div style="font-size:32px;font-weight:700;color:#2563eb;">{bmi}</div>
            <div style="font-size:12px;color:#16a34a;">{cat}</div>
        </div>
        <div style="background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);text-align:center;">
            <div style="font-size:13px;color:#64748b;margin-bottom:6px;">基础代谢 BMR</div>
            <div style="font-size:32px;font-weight:700;color:#7c3aed;">{bmr}</div>
            <div style="font-size:12px;color:#64748b;">kcal / 天</div>
        </div>
        <div style="background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);text-align:center;">
            <div style="font-size:13px;color:#64748b;margin-bottom:6px;">目标摄入</div>
            <div style="font-size:32px;font-weight:700;color:#ca8a04;">{target_kcal}</div>
            <div style="font-size:12px;color:#64748b;">kcal / 天</div>
        </div>
        <div style="background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);text-align:center;">
            <div style="font-size:13px;color:#64748b;margin-bottom:6px;">今日摄入</div>
            <div style="font-size:32px;font-weight:700;color:#16a34a;">{today_kcal}</div>
            <div style="font-size:12px;color:#64748b;">剩余 {remaining} kcal</div>
        </div>
    </div>
    """


def make_weekly_chart() -> plt.Figure:
    """Generate a 7-day calorie intake bar chart."""
    data = get_daily_summary(7)
    dates = [d["date"][-5:] for d in data]  # MM-DD
    values = [d["total_kcal"] for d in data]

    fig, ax = plt.subplots(figsize=(10, 3.5))
    colors = ["#ef4444" if v > 2000 else "#eab308" if v > 1800 else "#22c55e" for v in values]

    bars = ax.bar(range(7), values, color=colors, width=0.6, edgecolor="white", linewidth=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 15,
                str(val), ha="center", va="bottom", fontsize=9, fontweight="600", color="#334155")

    ax.set_xticks(range(7))
    ax.set_xticklabels(["一", "二", "三", "四", "五", "六", "日"], fontsize=10)
    ax.set_ylabel("热量 (kcal)", fontsize=10, color="#64748b")
    ax.set_ylim(0, max(values) * 1.3 + 50 if values else 2500)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#e2e8f0")
    ax.spines["bottom"].set_color("#e2e8f0")
    ax.tick_params(colors="#64748b")
    ax.grid(axis="y", alpha=0.3, color="#e2e8f0")

    plt.tight_layout()
    return fig


def make_today_table() -> list[list]:
    """Build today's meal records as a list of lists for gr.DataFrame."""
    records = get_meal_records(1)
    today = datetime.now().strftime("%Y-%m-%d")
    today_records = [r for r in records if (r.get("recorded_at") or "")[:10] == today]

    rows = []
    for r in today_records:
        time_str = (r.get("recorded_at") or "")[11:16] if r.get("recorded_at") else "--:--"
        rows.append([time_str, r["food_name"], f"{r['weight_grams']}g", f"{r['kcal']} kcal"])

    return rows if rows else [["--", "暂无记录", "--", "--"]]


def _bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "偏瘦"
    elif bmi < 24:
        return "正常范围"
    elif bmi < 28:
        return "偏重"
    return "肥胖"
```

---

### Task 8: Dashboard Layout

**Files:**
- Create: `ui/dashboard.py`

- [ ] **Step 1: Write ui/dashboard.py**

```python
"""Dashboard layout assembler."""
import gradio as gr

from ui.components import make_stat_card_html, make_weekly_chart, make_today_table
from services.supabase_client import get_user_profile
from utils.health_calc import calc_bmi, calc_bmr, calc_target_calories, calc_goal_from_weights


def build_dashboard() -> gr.Blocks:
    """Build and return the complete Gradio dashboard."""

    css = """
    .dashboard-wrap { max-width: 1200px; margin: 0 auto; }
    .gradio-container { max-width: 100% !important; }
    footer { display: none !important; }
    """

    with gr.Blocks(css=css, title="FitnessAI - 健康饮食管理") as app:
        gr.HTML("""
        <div style="text-align:center;padding:20px 0 10px;">
            <h1 style="font-size:28px;font-weight:700;margin:0;">🥦 FitnessAI</h1>
            <p style="color:#64748b;font-size:14px;margin:4px 0 0;">AI 驱动的健康饮食管理助手</p>
        </div>
        """)

        # ---- Stat cards ----
        stats_html = gr.HTML(visible=True)

        # ---- Profile section (collapsible) ----
        with gr.Accordion("⚙️ 个人档案", open=False):
            with gr.Row():
                gender = gr.Dropdown(choices=["男", "女"], label="性别", value="男")
                age = gr.Number(label="年龄", value=25, precision=0)
                height_cm = gr.Slider(140, 220, label="身高 (cm)", value=170)
                weight_kg = gr.Slider(30, 200, label="体重 (kg)", value=70)
                target_weight_kg = gr.Slider(30, 200, label="目标体重 (kg)", value=70)
                goal = gr.Dropdown(choices=["保持", "减重", "增重"], label="目标", value="保持")
            save_profile_btn = gr.Button("💾 保存档案", variant="primary")
            profile_msg = gr.Textbox(label="保存状态", visible=False)

        # ---- Food recognition ----
        with gr.Row():
            with gr.Column(scale=1):
                food_image = gr.Image(type="filepath", label="📸 上传食物图片", height=260)
                meal_type = gr.Dropdown(
                    choices=[("早餐", "breakfast"), ("午餐", "lunch"), ("晚餐", "dinner"), ("加餐", "snack")],
                    label="餐次", value="lunch"
                )
                recognize_btn = gr.Button("🔍 识别热量", variant="primary")

            with gr.Column(scale=1):
                recognition_result = gr.HTML(
                    '<div style="color:#94a3b8;text-align:center;padding:40px;">识别结果将显示在这里</div>'
                )
                save_meal_btn = gr.Button("💾 记录到今日饮食", variant="secondary", visible=False)

        # Hidden state to hold last recognized food data and meal type
        last_recognition = gr.State([])
        current_meal_type = gr.State("lunch")

        # ---- Weekly chart ----
        weekly_plot = gr.Plot(label="📊 近7天热量摄入趋势", value=make_weekly_chart)

        # ---- AI advice ----
        with gr.Row():
            diet_btn = gr.Button("🍽️ 饮食建议", variant="secondary")
            exercise_btn = gr.Button("🏃 运动指导", variant="secondary")
        advice_output = gr.Textbox(label="🤖 AI 建议", lines=8, interactive=False)

        # ---- Today's records ----
        today_table = gr.DataFrame(
            headers=["时间", "食物", "重量", "热量"],
            label="📝 今日饮食记录",
            value=make_today_table,
            interactive=False,
        )

        # ---- Refresh button ----
        refresh_btn = gr.Button("🔄 刷新仪表盘", variant="secondary")

        # ---- Event bindings ----

        def refresh_dashboard():
            profile = get_user_profile()
            if profile:
                bmi = calc_bmi(profile["height_cm"], profile["weight_kg"])
                bmr = calc_bmr(profile["gender"], profile["age"], profile["height_cm"], profile["weight_kg"])
                target = calc_target_calories(profile["gender"], profile["age"], profile["height_cm"], profile["weight_kg"], profile["goal"])
            else:
                bmi, bmr, target = 0, 0, 2000

            return (
                make_stat_card_html(bmi, bmr, target),
                make_weekly_chart(),
                make_today_table(),
            )

        refresh_btn.click(
            fn=refresh_dashboard,
            inputs=[],
            outputs=[stats_html, weekly_plot, today_table],
        )

        def refresh_profile():
            profile = get_user_profile()
            if profile:
                return (
                    profile["gender"], profile["age"], profile["height_cm"],
                    profile["weight_kg"], profile["target_weight_kg"], profile["goal"]
                )
            return "男", 25, 170, 70, 70, "保持"

        save_profile_btn.click(
            fn=_save_profile,
            inputs=[gender, age, height_cm, weight_kg, target_weight_kg],
            outputs=[goal, profile_msg],
        ).then(fn=refresh_dashboard, inputs=[], outputs=[stats_html, weekly_plot, today_table])

        weight_kg.change(fn=calc_goal_from_weights, inputs=[weight_kg, target_weight_kg], outputs=[goal])
        target_weight_kg.change(fn=calc_goal_from_weights, inputs=[weight_kg, target_weight_kg], outputs=[goal])

        recognize_btn.click(
            fn=_recognize_and_calculate,
            inputs=[food_image, meal_type],
            outputs=[recognition_result, save_meal_btn, last_recognition, current_meal_type],
        )

        save_meal_btn.click(
            fn=_save_meal,
            inputs=[last_recognition, current_meal_type],
            outputs=[recognition_result, save_meal_btn, today_table],
        ).then(fn=refresh_dashboard, inputs=[], outputs=[stats_html, weekly_plot, today_table])

        diet_btn.click(fn=_get_diet_advice, inputs=[], outputs=[advice_output])
        exercise_btn.click(fn=_get_exercise_advice, inputs=[], outputs=[advice_output])

        # Initial load
        app.load(fn=refresh_dashboard, inputs=[], outputs=[stats_html, weekly_plot, today_table])
        app.load(fn=refresh_profile, inputs=[], outputs=[gender, age, height_cm, weight_kg, target_weight_kg, goal])

    return app


def _save_profile(gender, age, height_cm, weight_kg, target_weight_kg):
    from services.supabase_client import upsert_user_profile
    from utils.health_calc import calc_goal_from_weights

    goal = calc_goal_from_weights(weight_kg, target_weight_kg)
    try:
        upsert_user_profile(gender, age, float(height_cm), float(weight_kg), float(target_weight_kg), goal)
        return goal, "✅ 保存成功"
    except Exception as e:
        return goal, f"❌ 保存失败: {e}"


def _recognize_and_calculate(image_path, meal_type):
    from services.food_recognition import recognize_food, review_food_data
    from services.supabase_client import search_food_kcal

    if not image_path:
        return '<div style="color:#ef4444;padding:20px;">请先上传图片</div>', gr.update(visible=False), [], meal_type

    try:
        raw = recognize_food(image_path)
        reviewed = review_food_data(raw)

        for item in reviewed:
            name = item.get("name", "")
            weight = item.get("weight", 0)
            kcal_per_100g = search_food_kcal(name)
            if kcal_per_100g:
                item["kcal"] = round(weight * 0.01 * kcal_per_100g, 1)

        rows = ""
        total = 0
        for item in reviewed:
            name = item.get("name", "?")
            weight = item.get("weight", 0)
            kcal = item.get("kcal", 0)
            total += kcal
            rows += f'<tr><td style="padding:6px 12px;">{name}</td><td style="padding:6px 12px;">{weight}g</td><td style="padding:6px 12px;text-align:right;">{kcal} kcal</td></tr>'

        html = f"""
        <div style="background:#f0fdf4;border-radius:12px;padding:16px;">
            <table style="width:100%;font-size:13px;border-collapse:collapse;">{rows}</table>
            <div style="border-top:1px solid #bbf7d0;margin-top:10px;padding-top:10px;font-weight:700;text-align:right;">
                合计: {round(total, 1)} kcal
            </div>
        </div>
        """
        return html, gr.update(visible=True), reviewed, meal_type
    except Exception as e:
        return f'<div style="color:#ef4444;padding:20px;">识别失败: {e}</div>', gr.update(visible=False), [], meal_type


def _save_meal(records, meal_type):
    from services.supabase_client import insert_meal_record

    if not records:
        return '<div style="color:#ef4444;padding:20px;">没有可保存的数据</div>', gr.update(visible=False), make_today_table()

    try:
        for item in records:
            insert_meal_record(
                food_name=item.get("name", "?"),
                weight_grams=int(item.get("weight", 0)),
                kcal=float(item.get("kcal", 0)),
                meal_type=meal_type,
            )
        return '<div style="color:#16a34a;text-align:center;padding:20px;">✅ 已保存到今日饮食</div>', gr.update(visible=False), make_today_table()
    except Exception as e:
        return f'<div style="color:#ef4444;padding:20px;">保存失败: {e}</div>', gr.update(visible=True), make_today_table()


def _get_diet_advice():
    from services.ai_advisor import get_diet_advice
    return get_diet_advice()


def _get_exercise_advice():
    from services.ai_advisor import get_exercise_advice
    return get_exercise_advice()
```

---

### Task 9: Main Entry Point (app_main.py)

**Files:**
- Create: `app_main.py` (at project root)

- [ ] **Step 1: Write app_main.py at project root**

```python
"""FitnessAI — AI-powered dietary health management.
Entry point: launches the Gradio dashboard.
"""
from ui.dashboard import build_dashboard

if __name__ == "__main__":
    app = build_dashboard()
    app.launch(server_name="127.0.0.1", server_port=7862, share=True)
```

---

### Task 10: README Rewrite

**Files:**
- Rewrite: `README.md`

- [ ] **Step 1: Write the new README**

```markdown
# 🥦 FitnessAI

**AI 驱动的健康饮食管理助手** — 拍照识别食物热量，智能跟踪每日摄入，获取个性化饮食和运动建议。

## 功能

- 📸 **AI 食物识别** — 拍照上传，千问 3.6 Plus 自动识别食物名称和重量
- 🔥 **热量计算** — 自动查询食物热量库，精准计算每餐摄入
- 📊 **可视化仪表盘** — BMI、BMR、今日摄入、7 天趋势图一目了然
- 🍽️ **饮食建议** — DeepSeek V4 Pro 基于你的饮食记录生成个性化建议
- 🏃 **运动指导** — 根据你的目标和饮食习惯推荐合适的运动方案
- 📝 **饮食记录** — 自动记录每餐数据，支持早/午/晚/加餐分类

## 项目结构

```
FitnessAI/
├── app_main.py              # Gradio 入口
├── config.py                # 环境变量配置
├── services/
│   ├── supabase_client.py   # Supabase 数据库操作
│   ├── food_recognition.py  # 千问 VL 食物识别
│   └── ai_advisor.py        # DeepSeek 饮食/运动建议
├── ui/
│   ├── components.py        # 可复用 UI 组件
│   └── dashboard.py         # 仪表盘布局
├── utils/
│   └── health_calc.py       # BMI/BMR/热量计算
├── prompts/                 # AI prompt 模板
├── images/                  # 示例图片
└── supabase_migration.sql   # 数据库建表 SQL
```

## 快速开始

### 1. 环境要求

- Python 3.11+
- Supabase 账号（免费版即可）

### 2. 配置 Supabase 数据库

1. 登录 [Supabase](https://supabase.com)，创建项目
2. 进入 SQL Editor，复制 `supabase_migration.sql` 的全部内容并执行
3. 在 Project Settings → API 中获取 `Project URL` 和 `service_role key`

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# DashScope（千问 VL 模型，用于食物识别）
DASHSCOPE_API_KEY=your-dashscope-api-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# DeepSeek（用于饮食/运动建议）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 启动

```bash
python app_main.py
```

浏览器打开 `http://127.0.0.1:7862` 即可使用。

## 使用流程

1. **设置档案** — 展开"个人档案"，填写性别、年龄、身高、体重、目标
2. **识别食物** — 上传食物照片，选择餐次，点击"识别热量"
3. **保存记录** — 确认识别结果后点击"记录到今日饮食"
4. **查看数据** — 仪表盘自动更新热量统计和趋势图
5. **获取建议** — 点击"饮食建议"或"运动指导"获取 AI 个性化方案

## 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | Gradio 5 |
| 数据库 | Supabase (PostgreSQL) |
| 食物识别 | Qwen 3.6 Plus (DashScope) |
| 饮食/运动建议 | DeepSeek V4 Pro |
| 图表 | Matplotlib |

## License

MIT
```

---

### Task 11: Clean Up Old Files

- [ ] **Step 1: Remove old demo directory (keep only what's migrated)**

```bash
rm -rf /Users/liuzihao/VibeCoding/FitnessAI/demo
```

This removes the old monolithic code — we've already migrated images, prompts, and replaced all functionality.

- [ ] **Step 2: Final directory verification**

```bash
find /Users/liuzihao/VibeCoding/FitnessAI -type f -not -path '*/.git/*' -not -path '*/.superpowers/*' -not -path '*/__pycache__/*' | sort
```

---

### Task 12: Install Dependencies & Test Launch

- [ ] **Step 1: Install dependencies**

```bash
cd /Users/liuzihao/VibeCoding/FitnessAI && pip install -r requirements.txt
```

- [ ] **Step 2: Verify imports work**

```bash
cd /Users/liuzihao/VibeCoding/FitnessAI && python -c "from config import SUPABASE_URL, DASHSCOPE_API_KEY, DEEPSEEK_API_KEY; print('Config OK')"
```

- [ ] **Step 3: Verify all modules import**

```bash
cd /Users/liuzihao/VibeCoding/FitnessAI && python -c "
from services.supabase_client import get_client
from services.food_recognition import recognize_food
from services.ai_advisor import get_diet_advice
from utils.health_calc import calc_bmi, calc_bmr, calc_target_calories
from ui.components import make_stat_card_html, make_weekly_chart
print('All imports OK')
"
```

- [ ] **Step 4: Test launch (will fail without .env, that's expected for import test)**

```bash
cd /Users/liuzihao/VibeCoding/FitnessAI && timeout 5 python app_main.py 2>&1 || true
```

---

### Task 13: Update Dockerfile

**Files:**
- Rewrite: `Dockerfile` (at project root)

- [ ] **Step 1: Write new Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7862

CMD ["python", "app_main.py"]
```
