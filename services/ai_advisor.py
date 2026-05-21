"""AI-powered diet and exercise advice via DeepSeek V4 Pro."""
import json

from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from services.supabase_client import get_meal_records, get_user_profile

client = None


def _get_client():
    global client
    if client is None:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return client


def get_diet_advice() -> str:
    """Generate personalized diet advice based on user profile and recent meals."""
    profile = get_user_profile()
    records = get_meal_records(7)

    if not profile:
        return "请先在仪表盘设置您的个人档案（性别、年龄、身高、体重、目标）。"

    user_info = (
        f"性别: {profile['gender']}, 年龄: {profile['age']}, "
        f"身高: {profile['height_cm']}cm, 体重: {profile['weight_kg']}kg, "
        f"目标: {profile['goal']}到{profile['target_weight_kg']}kg"
    )

    records_json = json.dumps(records, ensure_ascii=False, default=str)

    response = _get_client().chat.completions.create(
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
    """Generate personalized exercise guidance based on user profile and recent meals."""
    profile = get_user_profile()
    records = get_meal_records(7)

    if not profile:
        return "请先在仪表盘设置您的个人档案。"

    user_info = (
        f"性别: {profile['gender']}, 年龄: {profile['age']}, "
        f"身高: {profile['height_cm']}cm, 体重: {profile['weight_kg']}kg, "
        f"目标: {profile['goal']}到{profile['target_weight_kg']}kg"
    )

    records_json = json.dumps(records, ensure_ascii=False, default=str)

    response = _get_client().chat.completions.create(
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
