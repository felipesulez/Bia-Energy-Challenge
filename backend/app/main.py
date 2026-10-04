from fastapi import FastAPI

from app.routers.assignments import router as assignments_router


app = FastAPI()

app.include_router(assignments_router)


@app.get("/health")
def health():
    return {"status": "ok"}