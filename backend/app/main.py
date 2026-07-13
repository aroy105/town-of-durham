from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.ws.ws_routes import router as ws_router
from app.api.rest import router as rest_router

app = FastAPI(title="Town of Durham")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)

app.include_router(rest_router)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}