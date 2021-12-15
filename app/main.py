from fastapi import FastAPI
# from app.router import api_router
from app.routers import api_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Simply Jet Blog API",
    description="A simple Blog API of Simply Jet",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Simply Jet", "url": "https://simplyjet.com",
             "email": "ramananda.kairi@simply-jet.ch"},
    license={"name": "MIT", "url": "https://simplyjet.com"},
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", status_code=200, include_in_schema=False)
def root():
    return {"Simplyjet API": "Visit /docs to see the API List"}


app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    # Run the server
    uvicorn.run('main:app', host="localhost", port=8000,
                log_level="info", reload=True)
