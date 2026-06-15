# FuckUrticaria — 去他妈的荨麻疹

荨麻疹治疗管理平台，帮助记录、分析和战胜荨麻疹。

## 功能特性

- **发病记录** — 记录每次发作的时间、严重程度、诱因、部位和照片
- **趋势图表** — 可视化发病频率、严重度趋势、按时间段统计
- **用药管理** — 记录药物使用情况，追踪用药历史
- **UAS7 评分** — 基于 UAS7 标准的每日症状评分系统
- **生活打卡** — 记录睡眠、压力、运动、饮食等生活状态
- **天气追踪** — 自动抓取和风天气数据（温度、湿度、AQI、花粉等）
- **环境留档** — 每小时自动记录环境数据，生成趋势图表
- **AI 分析** — 基于历史数据的智能病情分析与建议
- **移动端适配** — 全界面响应式设计，支持 360px 及以上屏幕

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Vite + Tailwind CSS v4 |
| 后端 | FastAPI + SQLAlchemy 2.x + Pydantic v2 |
| 数据库 | MySQL 8.x |
| 天气 API | 和风天气（付费版） |
| 设计风格 | 手绘风格（Hand-Drawn UI） |

## 快速开始（Docker）

### 1. 准备环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入数据库密码、和风天气 API Key、访问密码等
```

### 2. 启动服务

```bash
docker compose up -d --build
```

服务启动后：
- 前端访问：`http://localhost`
- 后端 API：`http://localhost:5241/api/health`

### 3. 停止服务

```bash
docker compose down
```

## 开发环境

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # 编辑填入实际值
uvicorn main:app --reload --port 5241
```

### 前端

```bash
cd frontend
npm install
npm run dev                # 默认端口 2563
```

## 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `DB_HOST` | MySQL 主机地址 | `127.0.0.1` |
| `DB_PORT` | MySQL 端口 | `3306` |
| `DB_USER` | 数据库用户名 | `root` |
| `DB_PASSWORD` | 数据库密码 | |
| `DB_NAME` | 数据库名 | `UrticariaDb` |
| `QWEATHER_API_KEY` | 和风天气 API Key | |
| `QWEATHER_LOCATION_ID` | 和风天气位置 ID | `101230206` |
| `QWEATHER_CITY` | 城市名称 | `厦门集美` |
| `QWEATHER_API_DOMAIN` | API 域名（付费） | `api.qweather.com` |
| `ACCESS_PASSWORD` | 系统访问密码 | |
| `SECRET_KEY` | JWT 签名密钥 | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期（分钟） | `1440` |
| `CORS_ORIGINS` | 允许的跨域来源（逗号分隔） | `http://localhost:2563` |

## 端口说明

| 服务 | 端口 |
|------|------|
| 前端开发服务器 | 2563 |
| 后端 API | 5241 |
| Docker 前端 | 80 |
