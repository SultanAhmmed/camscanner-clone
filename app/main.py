# app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="CamScanner Clone API", version="0.1.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the CamScanner Clone API!"}

@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)
