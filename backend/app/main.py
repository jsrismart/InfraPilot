from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import api_router
from .core.config import settings

app = FastAPI(
    title="InfraPilot Backend",
    version="0.1.0",
    description="Clean backend template for InfraPilot"
)

# CORS - must be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# Include API
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {"message": "InfraPilot backend running"}

