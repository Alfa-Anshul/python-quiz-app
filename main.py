import hashlib, hmac, json, os, time, base64
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SECRET = b"kapil-anervea-secret-2024"
USERS = {"kapil": "Pass@123"}
NEWSDATAIO_URL = "https://newsdata.io/api/1/news"
NEWSDATAIO_KEY = os.getenv("NEWSDATAIO_KEY", "pub_demo")


def make_token(user: str) -> str:
    payload = json.dumps({"u": user, "t": int(time.time())}).encode()
    b64 = base64.urlsafe_b64encode(payload).rstrip(b"=")
    sig = hmac.new(SECRET, b64, hashlib.sha256).hexdigest()
    return f"{b64.decode()}.{sig}"


def verify_token(token: str, max_age: int = 3600):
    try:
        b64, sig = token.rsplit(".", 1)
        expected = hmac.new(SECRET, b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(b64 + "=="))
        if time.time() - payload["t"] > max_age:
            return None
        return payload["u"]
    except Exception:
        return None


def get_session(request: Request):
    token = request.cookies.get("session")
    return verify_token(token) if token else None


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse("/login" if not get_session(request) else "/news")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if USERS.get(username) == password:
        token = make_token(username)
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
        params = {"country": "us", "language": "en", "apikey": NEWSDATAIO_KEY}
        if category and category != "general":
            params["category"] = category
        if q:
            params["q"] = q
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(NEWSDATAIO_URL, params=params)
            articles = r.json().get("results", [])
    except Exception:
        articles = []
    return templates.TemplateResponse(
        "news.html",
        {"request": request, "articles": articles, "user": user, "category": category, "q": q}
    )
