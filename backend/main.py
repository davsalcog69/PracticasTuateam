from fastapi import FastAPI
from api.routes import router as api_router
from core.database import engine, Base
import models # Ensure all models are registered
from fastapi.middleware.cors import CORSMiddleware

# Create database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Car Import AI API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
def test():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Car Import AI API is online"}



app.include_router(api_router, prefix="/api")
