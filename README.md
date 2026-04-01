# 📰 NewsHub — kapil@anervea.live

A modern news web app built with FastAPI + Jinja2 + NewsData.io API.

## 🔐 Login Credentials
| Field | Value |
|---|---|
| Username | `kapil` |
| Password | `Pass@123` |

## 🚀 Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🐳 Run with Docker
```bash
cp .env.example .env   # add your NEWSDATAIO_KEY
docker-compose up -d
```

## 🌐 Domain
kapil@anervea.live

## 📡 API
[NewsData.io](https://newsdata.io) — free tier (200 req/day)
