from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app import models
from backend.app.database import Base, engine
from backend.app.auth_routes import router as auth_router
from backend.app.business_analytics import (
    analyze_sales,
    analyze_inventory,
)
from backend.app.agent.page_router import PageRouter
from backend.app.api_registry import (
    get_page_apis,
    list_page_apis,
)


# --------------------------------------------------
# Application initialization
# --------------------------------------------------

page_router = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global page_router

    # Create database tables for local development.
    Base.metadata.create_all(bind=engine)

    # Initialize the AI page router.
    page_router = PageRouter()

    try:
        yield
    finally:
        page_router = None


app = FastAPI(
    title="BizPilot AI",
    description="Context-aware business application agent",
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------------------------
# Authentication
# --------------------------------------------------

app.include_router(auth_router)


# --------------------------------------------------
# CORS configuration
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)


# --------------------------------------------------
# Request models
# --------------------------------------------------

class RouteRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural-language business request",
    )


# --------------------------------------------------
# Request latency middleware
# --------------------------------------------------

@app.middleware("http")
async def measure_request_latency(request: Request, call_next):
    started = perf_counter()

    response = await call_next(request)

    response.headers["X-Response-Time-ms"] = (
        f"{(perf_counter() - started) * 1000:.2f}"
    )

    return response


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "application": "BizPilot AI",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs",
    }


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "router_initialized": page_router is not None,
    }


# --------------------------------------------------
# API registry
# --------------------------------------------------

@app.get("/api/registry")
def api_registry():
    return {
        "application": "BizPilot AI",
        "pages": list_page_apis(),
    }


@app.get("/api/registry/{page_id}")
def page_api_registry(page_id: str):
    result = get_page_apis(page_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown page ID: {page_id}",
        )

    return result


# --------------------------------------------------
# AI page-routing endpoint
# --------------------------------------------------

@app.post("/api/route")
def route_request(request: RouteRequest):
    if page_router is None:
        raise HTTPException(
            status_code=503,
            detail="The routing engine is not initialized.",
        )

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=422,
            detail="Please enter a business request.",
        )

    try:
        result = page_router.route(query)

        return {
            "query": result["query"],
            "page_id": result["page_id"],
            "title": result.get("title"),
            "route": result["route"],
            "method": result["method"],
            "candidates": result.get("candidates", []),
        }

    except Exception:
        # Avoid exposing internal exception details.
        raise HTTPException(
            status_code=500,
            detail="The routing engine could not process the request.",
        ) from None


# --------------------------------------------------
# Sales analytics endpoint
# --------------------------------------------------

@app.get("/api/analytics/sales")
def sales_analytics():
    """Return calculated sales analytics."""

    try:
        return analyze_sales()

    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="The sales dataset is unavailable.",
        ) from None

    except (ValueError, KeyError):
        raise HTTPException(
            status_code=500,
            detail="The sales dataset contains invalid records.",
        ) from None


# --------------------------------------------------
# Inventory analytics endpoint
# --------------------------------------------------

@app.get("/api/analytics/inventory")
def inventory_analytics():
    """Return calculated inventory analytics."""

    try:
        return analyze_inventory()

    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="The inventory dataset is unavailable.",
        ) from None

    except (ValueError, KeyError):
        raise HTTPException(
            status_code=500,
            detail="The inventory dataset contains invalid records.",
        ) from None