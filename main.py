import hashlib, hmac, json, os, time, base64
import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()
SECRET = b"kapil-anervea-2024"
USERS = {"kapil": "Pass@123"}
NEWSDATAIO_URL = "https://newsdata.io/api/1/news"
NEWSDATAIO_KEY = os.getenv("NEWSDATAIO_KEY", "pub_demo")
CATS = ["general","world","business","technology","entertainment","sports","science","health"]

LOGIN_HTML = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NewsHub – Sign In</title>
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
body{{min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,#0f2027 0%,#203a43 50%,#2c5364 100%);
  font-family:'Segoe UI',system-ui,sans-serif}}
.card{{background:rgba(255,255,255,0.07);backdrop-filter:blur(16px);
  border:1px solid rgba(255,255,255,0.15);border-radius:24px;
  padding:52px 44px;width:400px;box-shadow:0 24px 64px rgba(0,0,0,0.5)}}
.logo{{text-align:center;margin-bottom:36px}}
.icon{{font-size:3rem;margin-bottom:8px}}
h1{{color:#fff;font-size:2rem;font-weight:800;letter-spacing:-1px}}
h1 span{{color:#38bdf8}}
.sub{{color:#64748b;font-size:.85rem;margin-top:6px}}
.field{{margin-bottom:20px}}
label{{display:block;color:#94a3b8;font-size:.78rem;font-weight:700;
  letter-spacing:.8px;text-transform:uppercase;margin-bottom:7px}}
input{{width:100%;padding:13px 16px;border-radius:12px;
  border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.07);
  color:#fff;font-size:.95rem;outline:none;transition:all .2s}}
input::placeholder{{color:#475569}}
input:focus{{border-color:#38bdf8;background:rgba(56,189,248,0.08);
  box-shadow:0 0 0 3px rgba(56,189,248,0.12)}}
.btn{{width:100%;padding:14px;border:none;border-radius:12px;
  background:linear-gradient(90deg,#0ea5e9,#6366f1);
  color:#fff;font-size:1rem;font-weight:700;cursor:pointer;
  letter-spacing:.3px;transition:all .2s;margin-top:8px}}
.btn:hover{{opacity:.92;transform:translateY(-2px);box-shadow:0 8px 24px rgba(14,165,233,0.4)}}
.error{{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.35);
  color:#fca5a5;padding:11px 16px;border-radius:10px;
  font-size:.84rem;margin-bottom:20px;text-align:center}}
.footer{{text-align:center;color:#334155;font-size:.75rem;
  margin-top:24px;border-top:1px solid rgba(255,255,255,0.08);padding-top:20px}}
</style></head><body>
<div class="card">
  <div class="logo">
    <div class="icon">📰</div>
    <h1>News<span>Hub</span></h1>
    <p class="sub">Your premium daily news experience</p>
  </div>
  {error_html}
  <form method="post" action="/login">
    <div class="field"><label for="u">Username</label>
      <input id="u" type="text" name="username" placeholder="Enter your username" required autocomplete="username"/></div>
    <div class="field"><label for="p">Password</label>
      <input id="p" type="password" name="password" placeholder="Enter your password" required autocomplete="current-password"/></div>
    <button class="btn" type="submit">Sign In →</button>
  </form>
  <div class="footer">🌐 kapil@anervea.live &nbsp;·&nbsp; Powered by Anervea</div>
</div></body></html>
"""

NEWS_HTML_TOP = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NewsHub – Headlines</title>
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0f1e;font-family:'Segoe UI',system-ui,sans-serif;color:#e2e8f0;min-height:100vh}}
nav{{background:linear-gradient(90deg,#0f2027,#1e3a5f);padding:0 32px;
  display:flex;align-items:center;justify-content:space-between;
  height:68px;position:sticky;top:0;z-index:100;
  box-shadow:0 2px 20px rgba(0,0,0,0.5);border-bottom:1px solid rgba(255,255,255,0.06)}}
.brand{{font-size:1.5rem;font-weight:800;color:#fff}}
.brand span{{color:#38bdf8}}
.nav-right{{display:flex;align-items:center;gap:16px}}
.chip{{background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.25);
  padding:6px 14px;border-radius:20px;font-size:.82rem;color:#7dd3fc}}
.logout{{padding:7px 16px;border-radius:8px;background:rgba(239,68,68,0.12);
  color:#fca5a5;text-decoration:none;font-size:.82rem;font-weight:600;
  border:1px solid rgba(239,68,68,0.25);transition:.2s}}
.logout:hover{{background:rgba(239,68,68,0.28)}}
.hero{{background:linear-gradient(135deg,#0f2027,#1a3a5c);padding:32px;
  text-align:center;border-bottom:1px solid rgba(255,255,255,0.06)}}
.hero h2{{font-size:1.6rem;font-weight:700;color:#fff;margin-bottom:4px}}
.hero p{{color:#64748b;font-size:.88rem}}
.wrap{{max-width:1280px;margin:0 auto;padding:28px 20px}}
.sbar{{display:flex;gap:10px;margin-bottom:24px}}
.sbar input{{flex:1;padding:12px 18px;border-radius:12px;
  border:1px solid rgba(255,255,255,0.12);
  background:rgba(255,255,255,0.05);color:#fff;font-size:.95rem;outline:none;transition:.2s}}
.sbar input:focus{{border-color:#38bdf8}}
.sbar button{{padding:12px 24px;border:none;border-radius:12px;
  background:linear-gradient(90deg,#0ea5e9,#6366f1);color:#fff;font-weight:700;cursor:pointer}}
.cats{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:32px}}
.cat{{padding:8px 18px;border-radius:20px;border:1px solid rgba(255,255,255,0.12);
  color:#64748b;text-decoration:none;font-size:.8rem;font-weight:600;transition:.2s}}
.cat:hover{{border-color:#38bdf8;color:#38bdf8}}
.cat.on{{background:linear-gradient(90deg,#0ea5e9,#6366f1);color:#fff;
  border-color:transparent;box-shadow:0 4px 12px rgba(14,165,233,0.3)}}
.lbl{{font-size:.78rem;font-weight:700;color:#475569;letter-spacing:.5px;text-transform:uppercase;margin-bottom:20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}}
.card{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
  border-radius:18px;overflow:hidden;display:flex;flex-direction:column;transition:all .25s}}
.card:hover{{transform:translateY(-5px);box-shadow:0 16px 48px rgba(0,0,0,0.4);
  border-color:rgba(56,189,248,0.25)}}
.card img{{width:100%;height:185px;object-fit:cover}}
.cb{{padding:20px;flex:1;display:flex;flex-direction:column;gap:10px}}
.meta{{display:flex;align-items:center;justify-content:space-between}}
.src{{font-size:.7rem;color:#38bdf8;font-weight:700;text-transform:uppercase;letter-spacing:.8px}}
.dt{{font-size:.7rem;color:#334155}}
.ttl{{font-size:.97rem;font-weight:700;color:#f1f5f9;line-height:1.45}}
.dsc{{font-size:.82rem;color:#64748b;flex:1;line-height:1.55}}
.rl{{margin-top:auto;display:inline-flex;align-items:center;gap:6px;
  padding:8px 16px;border-radius:8px;background:rgba(14,165,233,0.1);color:#38bdf8;
  text-decoration:none;font-size:.8rem;font-weight:600;
  border:1px solid rgba(14,165,233,0.2);transition:.2s;width:fit-content}}
.rl:hover{{background:#0ea5e9;color:#fff}}
.empty{{text-align:center;padding:100px 20px;color:#334155}}
.empty .big{{font-size:3rem;margin-bottom:12px}}
footer{{text-align:center;padding:32px;color:#1e293b;font-size:.78rem;
  border-top:1px solid rgba(255,255,255,0.04);margin-top:48px}}
</style></head><body>
"""


def make_token(user):
    payload = json.dumps({"u": user, "t": int(time.time())}).encode()
    b64 = base64.urlsafe_b64encode(payload).rstrip(b"=")
    sig = hmac.new(SECRET, b64, hashlib.sha256).hexdigest()
    return f"{b64.decode()}.{sig}"


def verify_token(token, max_age=3600):
    try:
        b64, sig = token.rsplit(".", 1)
        exp = hmac.new(SECRET, b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, exp):
            return None
        payload = json.loads(base64.urlsafe_b64decode(b64 + "=="))
        if time.time() - payload["t"] > max_age:
            return None
        return payload["u"]
    except Exception:
        return None


def get_session(request):
    t = request.cookies.get("session")
    return verify_token(t) if t else None


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse("/login" if not get_session(request) else "/news")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    html = LOGIN_HTML.format(error_html="")
    return HTMLResponse(html)


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if USERS.get(username) == password:
        resp = RedirectResponse("/news", status_code=302)
        resp.set_cookie("session", make_token(username), httponly=True, max_age=3600)
        return resp
    err = '<div class="error">⚠️ Invalid credentials. Please try again.</div>'
    return HTMLResponse(LOGIN_HTML.format(error_html=err))


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

    # Build nav
    out = NEWS_HTML_TOP
    out += f'<nav><div class="brand">📰 News<span>Hub</span></div>'
    out += f'<div class="nav-right"><span class="chip">👤 {user}</span>'
    out += '<a href="/logout" class="logout">Logout</a></div></nav>'
    out += '<div class="hero"><h2>Today\'s Top Headlines</h2><p>Stay informed with the latest news from around the world</p></div>'
    out += '<div class="wrap">'

    # Search bar
    out += f'<form method="get" action="/news" class="sbar">'
    out += f'<input type="hidden" name="category" value="{category}"/>'
    out += f'<input type="text" name="q" value="{q}" placeholder="🔍 Search for news topics..."/>'
    out += '<button type="submit">Search</button></form>'

    # Categories
    out += '<div class="cats">'
    for cat in CATS:
        cls = "cat on" if cat == category else "cat"
        out += f'<a href="/news?category={cat}" class="{cls}">{cat.capitalize()}</a>'
    out += '</div>'

    # Articles
    if articles:
        n = len(articles)
        out += f'<div class="lbl">{n} article{"s" if n != 1 else ""} found</div>'
        out += '<div class="grid">'
        for a in articles:
            title = (a.get("title") or "").replace("<","&lt;").replace(">","&gt;")
            desc = (a.get("description") or "")[:160].replace("<","&lt;").replace(">","&gt;")
            src = (a.get("source_id") or "News").replace("<","&lt;")
            date = (a.get("pubDate") or "")[:10]
            link = a.get("link") or "#"
            img = a.get("image_url") or ""
            out += '<div class="card">'
            if img:
                out += f'<img src="{img}" alt="" loading="lazy" onerror="this.style.display=\'none\'"/>'
            out += f'<div class="cb"><div class="meta"><span class="src">{src}</span><span class="dt">{date}</span></div>'
            out += f'<div class="ttl">{title}</div><div class="dsc">{desc}</div>'
            out += f'<a href="{link}" target="_blank" rel="noopener" class="rl">Read more →</a></div></div>'
        out += '</div>'
    else:
        out += '<div class="empty"><div class="big">📡</div><p>No articles found. Check your API key or try a different category.</p></div>'

    out += '</div><footer>NewsHub &copy; 2024 &nbsp;&middot;&nbsp; kapil@anervea.live &nbsp;&middot;&nbsp; Powered by Anervea</footer></body></html>'
    return HTMLResponse(out)
