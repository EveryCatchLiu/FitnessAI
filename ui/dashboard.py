"""Dashboard layout assembler for FitnessAI."""
import gradio as gr

from ui.components import make_stat_card_html, make_weekly_chart, make_today_table
from services.supabase_client import get_user_profile, upsert_user_profile, insert_meal_record, search_food_kcal
from utils.health_calc import calc_bmi, calc_bmr, calc_target_calories, calc_goal_from_weights


def build_dashboard() -> gr.Blocks:
    """Build and return the complete Gradio dashboard."""

    with gr.Blocks(title="FitnessAI - 健康饮食管理") as app:
        gr.HTML("""
        <style>
        .dashboard-wrap { max-width: 1200px; margin: 0 auto; }
        .gradio-container { max-width: 100% !important; }
        footer { display: none !important; }
        </style>
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
            profile_msg = gr.Textbox(label="", visible=False)

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

        # ======== Event Bindings ========

        def refresh_dashboard():
            profile = get_user_profile()
            if profile:
                bmi = calc_bmi(profile["height_cm"], profile["weight_kg"])
                bmr = calc_bmr(profile["gender"], profile["age"], profile["height_cm"], profile["weight_kg"])
                target = calc_target_calories(
                    profile["gender"], profile["age"], profile["height_cm"],
                    profile["weight_kg"], profile["goal"]
                )
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

        def save_profile(gender_val, age_val, height_val, weight_val, target_val):
            goal_val = calc_goal_from_weights(weight_val, target_val)
            try:
                upsert_user_profile(gender_val, age_val, float(height_val), float(weight_val), float(target_val), goal_val)
                return goal_val, "✅ 保存成功"
            except Exception as e:
                return goal_val, f"❌ 保存失败: {e}"

        save_profile_btn.click(
            fn=save_profile,
            inputs=[gender, age, height_cm, weight_kg, target_weight_kg],
            outputs=[goal, profile_msg],
        ).then(fn=refresh_dashboard, inputs=[], outputs=[stats_html, weekly_plot, today_table])

        weight_kg.change(fn=calc_goal_from_weights, inputs=[weight_kg, target_weight_kg], outputs=[goal])
        target_weight_kg.change(fn=calc_goal_from_weights, inputs=[weight_kg, target_weight_kg], outputs=[goal])

        def recognize_and_calculate(image_path, meal_type_val):
            from services.food_recognition import recognize_food, review_food_data

            if not image_path:
                return (
                    '<div style="color:#ef4444;padding:20px;">请先上传图片</div>',
                    gr.update(visible=False), [], meal_type_val
                )

            try:
                raw = recognize_food(image_path)
                reviewed = review_food_data(raw)

                for item in reviewed:
                    name = item.get("name", "")
                    weight = item.get("weight", 0)
                    kcal_per_100g = search_food_kcal(name)
                    if kcal_per_100g:
                        item["kcal"] = round(weight * 0.01 * kcal_per_100g, 1)
                    else:
                        item["kcal"] = item.get("kcal", 0)

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
                return html, gr.update(visible=True), reviewed, meal_type_val
            except Exception as e:
                return (
                    f'<div style="color:#ef4444;padding:20px;">识别失败: {e}</div>',
                    gr.update(visible=False), [], meal_type_val
                )

        recognize_btn.click(
            fn=recognize_and_calculate,
            inputs=[food_image, meal_type],
            outputs=[recognition_result, save_meal_btn, last_recognition, current_meal_type],
        )

        def save_meal(records, meal_type_val):
            if not records:
                return (
                    '<div style="color:#ef4444;padding:20px;">没有可保存的数据</div>',
                    gr.update(visible=False), make_today_table()
                )

            try:
                for item in records:
                    insert_meal_record(
                        food_name=item.get("name", "?"),
                        weight_grams=int(item.get("weight", 0)),
                        kcal=float(item.get("kcal", 0)),
                        meal_type=meal_type_val,
                    )
                return (
                    '<div style="color:#16a34a;text-align:center;padding:20px;">✅ 已保存到今日饮食</div>',
                    gr.update(visible=False), make_today_table()
                )
            except Exception as e:
                return (
                    f'<div style="color:#ef4444;padding:20px;">保存失败: {e}</div>',
                    gr.update(visible=True), make_today_table()
                )

        save_meal_btn.click(
            fn=save_meal,
            inputs=[last_recognition, current_meal_type],
            outputs=[recognition_result, save_meal_btn, today_table],
        ).then(fn=refresh_dashboard, inputs=[], outputs=[stats_html, weekly_plot, today_table])

        def get_diet_advice():
            from services.ai_advisor import get_diet_advice as _diet
            return _diet()

        def get_exercise_advice():
            from services.ai_advisor import get_exercise_advice as _exercise
            return _exercise()

        diet_btn.click(fn=get_diet_advice, inputs=[], outputs=[advice_output])
        exercise_btn.click(fn=get_exercise_advice, inputs=[], outputs=[advice_output])

        # Initial load
        app.load(fn=refresh_dashboard, inputs=[], outputs=[stats_html, weekly_plot, today_table])
        app.load(fn=refresh_profile, inputs=[], outputs=[gender, age, height_cm, weight_kg, target_weight_kg, goal])

    return app
