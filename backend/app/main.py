from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.assignments import router as assignments_router


app = FastAPI(
    title="Motor de Asignación Comercial",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assignments_router)


@app.get("/health")
def health():
    return {"status": "ok"}