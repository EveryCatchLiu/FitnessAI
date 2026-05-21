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
    """Calculate daily calorie target based on goal (减重/增重/保持 or lose/gain/maintain)."""
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
