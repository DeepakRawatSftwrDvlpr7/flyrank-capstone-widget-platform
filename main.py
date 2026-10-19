import sqlite3
import httpx
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize SQLite Database
def init_db():
    with sqlite3.connect("platform.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, token TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS widgets (id TEXT PRIMARY KEY, owner_id INTEGER, title TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            widget_id TEXT, email TEXT, country TEXT, 
            FOREIGN KEY(widget_id) REFERENCES widgets(id)
        )''')
        # Seed dummy user and widget for testing
        conn.execute("INSERT OR IGNORE INTO users (id, token) VALUES (1, 'secret-admin-token')")
        conn.execute("INSERT OR IGNORE INTO widgets (id, owner_id, title) VALUES ('w_123', 1, 'My Signup')")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Widget Platform Capstone", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Stage: CORS configuration for public widget submissions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class SubmissionPayload(BaseModel):
    email: EmailStr
    honeypot: Optional[str] = None  # Spam prevention

# --- Auth Dependency ---
def verify_owner(authorization: str = Header(None)):
    if authorization != "Bearer secret-admin-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return 1

# --- 1 & 6. Widget Management & Dashboard ---
@app.get("/api/dashboard", dependencies=[Depends(verify_owner)])
def get_dashboard():
    with sqlite3.connect("platform.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM submissions ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]

# --- 2 & 3. Embed Delivery (Cached) ---
@app.get("/widget.js")
def serve_widget():
    # Cache headers like a CDN
    return FileResponse("widget.js", media_type="application/javascript", headers={"Cache-Control": "public, max-age=3600"})

# --- 4 & 5. Hardened Public Submission API ---
async def get_geo_location(ip: str) -> str:
    # Enrichment Fallback Chain: Provider A -> Provider B -> Unknown
    if ip == "127.0.0.1": return "Localhost"
    
    async with httpx.AsyncClient() as client:
        try:
            # Provider A: ip-api.com
            resp = await client.get(f"http://ip-api.com/json/{ip}", timeout=2.0)
            if resp.status_code == 200 and resp.json().get("status") == "success":
                return resp.json().get("country", "Unknown")
        except Exception:
            pass
            
        try:
            # Provider B: ipapi.co (Fallback)
            resp = await client.get(f"https://ipapi.co/{ip}/json/", timeout=2.0)
            if resp.status_code == 200:
                return resp.json().get("country_name", "Unknown")
        except Exception:
            return "Unknown"
    return "Unknown"

def send_confirmation_email_side_effect():
    # Failing side effect that must not crash the main path
    raise Exception("SMTP Server Down")

@app.post("/api/submit/{widget_id}")
@limiter.limit("5/minute")
async def handle_submission(widget_id: str, payload: SubmissionPayload, request: Request):
    # Abuse Protection: Honeypot Check
    if payload.honeypot:
        return JSONResponse(status_code=400, content={"error": "Spam detected"})

    # Enrichment
    client_ip = request.client.host
    country = await get_geo_location(client_ip)

    # Database Store
    with sqlite3.connect("platform.db") as conn:
        conn.execute("INSERT INTO submissions (widget_id, email, country) VALUES (?, ?, ?)", 
                     (widget_id, payload.email, country))
        conn.commit()

    # Safe Side Effect
    try:
        send_confirmation_email_side_effect()
    except Exception:
        pass # Degrade gracefully

    return {"status": "success", "message": "Submission recorded", "enriched_country": country}
