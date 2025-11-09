from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Simple FastAPI app for Vercel
app = FastAPI(title="Our Area API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Our Area API is running on Vercel", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}