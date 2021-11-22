from fastapi import FastAPI
# from app.router import api_router
from app.routers import api_router


app = FastAPI()


app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    # Run the server
    uvicorn.run('main:app', host="localhost", port=8000,
                log_level="info", reload=True)
