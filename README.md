# 🥦 FitnessAI

**AI 驱动的健康饮食管理助手** — 拍照识别食物热量，智能跟踪每日摄入，获取个性化饮食和运动建议。

## 功能

- 📸 **AI 食物识别** — 拍照上传，Qwen VL Plus 自动识别食物名称、份量和热量
- 🔥 **热量复核** — 二次 AI 审核识别结果，修正不合理的热量估算
- 📊 **可视化仪表盘** — BMI、BMR、每日目标、今日摄入、7 天趋势图一目了然
- 🍽️ **饮食建议** — DeepSeek V4 Pro 基于你的饮食记录生成个性化建议（Markdown 渲染）
- 🏃 **运动指导** — 根据你的目标和饮食习惯推荐合适的运动方案（Markdown 渲染）
- 📝 **饮食记录** — 自动记录每餐数据，支持早/午/晚/加餐分类，支持删除记录
- 🎨 **优雅 UI** — 纯 HTML/CSS/JS 前端，Chart.js 图表，Cormorant Garamond 字体

## 项目结构

```
FitnessAI/
├── app_main.py              # FastAPI 入口
├── api.py                   # REST API 路由
├── config.py                # 环境变量配置
├── services/
│   ├── supabase_client.py   # Supabase 数据库操作
│   ├── food_recognition.py  # Qwen VL 食物识别 + 热量复核
│   └── ai_advisor.py        # DeepSeek 饮食/运动建议
├── ui/
│   ├── components.py        # 可复用 UI 组件
│   └── dashboard.py         # 仪表盘布局
├── utils/
│   └── health_calc.py       # BMI/BMR/热量计算
├── static/
│   └── index.html           # 前端页面（含 Chart.js + Markdown 渲染）
├── prompts/                 # AI prompt 模板
├── images/                  # 示例图片
└── supabase_migration.sql   # 数据库建表 SQL
```

## 快速开始

### 1. 环境要求

- Python 3.11+
- Supabase 账号（[免费注册](https://supabase.com)）

### 2. 配置 Supabase 数据库

1. 登录 [Supabase](https://supabase.com)，创建新项目
2. 进入 **SQL Editor**，将 `supabase_migration.sql` 的全部内容粘贴并执行
3. 在 **Project Settings → API** 中获取：
   - `Project URL`（即 `SUPABASE_URL`）
   - `service_role key`（即 `SUPABASE_SERVICE_ROLE_KEY`）

### 3. 配置 API Key

你需要以下 API Key：

| 服务 | 用途 | 获取地址 |
|------|------|----------|
| DashScope | Qwen VL 食物识别 + 热量复核 | [阿里云百炼](https://bailian.console.aliyun.com/) |
| DeepSeek | 饮食/运动建议 | [DeepSeek Platform](https://platform.deepseek.com/) |

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际的 API Key：

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

### 5. 安装依赖

```bash
pip install -r requirements.txt
```

### 6. 启动

```bash
python app_main.py
```

浏览器打开 `http://127.0.0.1:7862` 即可使用。

## 使用流程

1. **设置档案** — 点击「个人档案」，填写性别、年龄、身高、体重、目标体重
2. **识别食物** — 上传食物照片，选择餐次（早/午/晚/加餐），点击「识别热量」
3. **保存记录** — 确认识别结果后点击「记录到今日饮食」，统计卡片自动更新
4. **查看数据** — 仪表盘自动更新热量统计卡片、7 天趋势图和今日饮食表
5. **删除记录** — 点击饮食记录旁的 ✕ 按钮即可删除单条记录
6. **获取建议** — 点击「饮食建议」或「运动指导」获取 AI 个性化方案（支持 Markdown 排版）

## Docker 部署

```bash
docker build -t fitness-ai .
docker run -p 7862:7862 --env-file .env fitness-ai
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 前端 | 原生 HTML/CSS/JS |
| 数据库 | Supabase (PostgreSQL) |
| 图表 | Chart.js |
| 食物识别 | Qwen VL Plus (DashScope) |
| 热量复核 | Qwen Plus (DashScope) |
| 饮食/运动建议 | DeepSeek V4 Pro |
| Markdown 渲染 | marked.js |

## License

MIT
