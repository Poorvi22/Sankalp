from fastapi import FastAPI
from fastapi.testclient import TestClient

print("STEP 1: Importing database...")
from backend.app.database import Base, engine

print("STEP 2: Importing models...")
from backend.app import models

print("STEP 3: Importing authentication routes...")
from backend.app.auth_routes import router as auth_router

print("STEP 4: Importing page router...")
from backend.app.agent.page_router import PageRouter

print("STEP 5: Importing API registry...")
from backend.app.api_registry import list_page_apis, get_page_apis

print("STEP 6: Creating test application...")
app = FastAPI()
app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}


print("STEP 7: Testing health endpoint...")

with TestClient(app) as client:
    response = client.get("/health")
    print("Health status:", response.status_code)
    print("Health response:", response.json())

print("DIAGNOSTIC COMPLETE")