from fastapi import FastAPI

app = FastAPI(title="Car Arbitration API")

@app.get("/")
async def root():
    return {"message": "API is online"}
