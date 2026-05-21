"""Reusable Gradio UI components."""
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime

# Use CJK-capable font for Chinese chart labels
_cjk_font = None
for name in ["PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS", "Noto Sans CJK SC"]:
    for f in fm.fontManager.ttflist:
        if f.name == name:
            _cjk_font = f
            break
    if _cjk_font:
        break

if _cjk_font:
    plt.rcParams["font.family"] = _cjk_font.name
    plt.rcParams["font.sans-serif"] = [_cjk_font.name]
plt.rcParams["axes.unicode_minus"] = False

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
    """Generate a 7-day calorie intake bar chart as a matplotlib Figure."""
    data = get_daily_summary(7)
    # Use MM-DD format for x-axis labels
    dates = [d["date"][-5:] for d in data]
    values = [d["total_kcal"] for d in data]

    fig, ax = plt.subplots(figsize=(10, 3.5))
    # Color bars: red if over 2000, yellow if over 1800, green otherwise
    colors = ["#ef4444" if v > 2000 else "#eab308" if v > 1800 else "#22c55e" for v in values]

    bars = ax.bar(range(7), values, color=colors, width=0.6, edgecolor="white", linewidth=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 15,
                str(val), ha="center", va="bottom", fontsize=9, fontweight="600", color="#334155")

    ax.set_xticks(range(7))
    ax.set_xticklabels(["一", "二", "三", "四", "五", "六", "日"], fontsize=10)
    ax.set_ylabel("热量 (kcal)", fontsize=10, color="#64748b")
    max_val = max(values) if values else 2500
    ax.set_ylim(0, max_val * 1.3 + 50)
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
