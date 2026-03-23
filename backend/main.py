from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv
import jwt, os
from pydantic import BaseModel
from typing import Optional
from datetime import date

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hireiq-mu.vercel.app"],  # Replace with your Vercel URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ── Auth helper ──
def get_user_id(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"], options={"verify_aud": False})
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── Schemas ──
class JobCreate(BaseModel):
    company: str
    role: str
    location: Optional[str] = None
    salary: Optional[str] = None
    status: str = "saved"
    applied_date: Optional[str] = None
    job_description: Optional[str] = None
    notes: Optional[str] = None

# ── Routes ──
@app.get("/jobs")
def get_jobs(user_id: str = Depends(get_user_id)):
    res = supabase.table("jobs").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data

@app.post("/jobs")
def create_job(job: JobCreate, user_id: str = Depends(get_user_id)):
    res = supabase.table("jobs").insert({**job.dict(), "user_id": user_id}).execute()
    return res.data[0]

@app.put("/jobs/{job_id}")
def update_job(job_id: str, job: JobCreate, user_id: str = Depends(get_user_id)):
    res = supabase.table("jobs").update(job.dict()).eq("id", job_id).eq("user_id", user_id).execute()
    return res.data[0]

@app.delete("/jobs/{job_id}")
def delete_job(job_id: str, user_id: str = Depends(get_user_id)):
    supabase.table("jobs").delete().eq("id", job_id).eq("user_id", user_id).execute()
    return {"ok": True}

@app.get("/health")
def health():
    return {"status": "ok"}