"""Food image recognition via Qwen VL (DashScope)."""
import base64
import json
import re
import logging

from openai import OpenAI

from config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, BASE_DIR

logger = logging.getLogger(__name__)

client = None


def _get_client():
    global client
    if client is None:
        client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL)
    return client


def _load_prompt(name: str) -> str:
    path = BASE_DIR / "prompts" / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _extract_json(text: str) -> list[dict]:
    """Extract JSON list from markdown-wrapped or plain text response."""
    clean = re.sub(r'```(?:json)?\s*|```', '', text).strip()

    # Try to find a JSON array: [{...}, ...]
    match = re.search(r'\[\s*\{.*?\}\s*\]', clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Fall back to single JSON object: {...}
    match = re.search(r'\{\s*".*?\}\s*', clean, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(0))
            if isinstance(result, dict):
                return [result]
        except json.JSONDecodeError:
            pass

    return []


def recognize_food(image_path: str) -> list[dict]:
    """Analyze food image using Qwen VL and return list of {name, weight} dicts."""
    prompt = _load_prompt("food_detection.txt")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    response = _get_client().chat.completions.create(
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
    logger.info("Food recognition raw response length: %d", len(content) if content else 0)
    return _extract_json(content)


def review_food_data(raw_data: list[dict]) -> list[dict]:
    """Second-pass review of food data for calorie sanity check via Qwen."""
    if not raw_data:
        return raw_data

    prompt = _load_prompt("food_review.txt")

    try:
        response = _get_client().chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(raw_data, ensure_ascii=False)}
            ]
        )
    except Exception as e:
        logger.warning("Review API call failed: %s, using raw data", e)
        return raw_data

    content = response.choices[0].message.content
    if not content:
        return raw_data

    corrected = _extract_json(content)
    if corrected:
        return corrected

    return raw_data
