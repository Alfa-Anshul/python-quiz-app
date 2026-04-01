from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeTimedSerializer, BadSignature
import httpx, os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SECRET = "kapil-anervea-secret-2024"
SERIALIZER = URLSafeTimedSerializer(SECRET)
USERS = {"kapil": "Pass@123"}

NEWSDATAIO_URL = "https://newsdata.io/api/1/news"
NEWSDATAIO_KEY = os.getenv("NEWSDATAIO_KEY", "pub_demo")


def get_session(request: Request):
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        return SERIALIZER.loads(token, max_age=3600).get("user")
    except BadSignature:
        return None


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse("/login" if not get_session(request) else "/news")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if USERS.get(username) == password:
        token = SERIALIZER.dumps({"user": username})
        resp = RedirectResponse("/news", status_code=302)
        resp.set_cookie("session", token, httponly=True, max_age=3600)
        return resp
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials. Please try again."})


@app.get("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie("session")
    return resp


@app.get("/news", response_class=HTMLResponse)
async def news(request: Request, category: str = "general", q: str = ""):
    user = get_session(request)
    if not user:
        return RedirectResponse("/login")
    articles = []
    try:
        params = {
            "country": "us",
            "language": "en",
            "apikey": NEWSDATAIO_KEY,
        }
        if category and category != "general":
            params["category"] = category
        if q:
            params["q"] = q
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(NEWSDATAIO_URL, params=params)
            data = r.json()
            articles = data.get("results", [])
    except Exception as e:
        articles = []
    return templates.TemplateResponse(
        "news.html",
        {"request": request, "articles": articles, "user": user, "category": category, "q": q}
    )
