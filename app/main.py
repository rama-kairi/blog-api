from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api_router

app = FastAPI(
    title="Simply Jet Blog API",
    description="A simple Blog API of Simply Jet",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Simply Jet",
        "url": "https://simplyjet.com",
        "email": "ramananda.kairi@simply-jet.ch",
    },
    license={"name": "MIT", "url": "https://simplyjet.com"},
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=200, include_in_schema=False)
def root():
    return {"Simplyjet API": "Visit /docs to see the API List"}


app.include_router(api_router, prefix="/api/v1")
