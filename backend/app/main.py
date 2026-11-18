
from fastapi import FastAPI

app = FastAPI(
    title="PhishGuard X API",
    description="AI-powered phishing detection and browser protection platform",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to PhishGuard X",
        "status": "running"
    }

@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "service": "PhishGuard X Backend"
    }
