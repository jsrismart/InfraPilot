from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def status():
    return {"status": "ok", "service": "InfraPilot Backend"}

@router.get("/check")
def check():
    return {"status": "ok", "service": "InfraPilot Backend"}
