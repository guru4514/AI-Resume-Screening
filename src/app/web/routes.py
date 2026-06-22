from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["dashboard"])


@router.get("/")
def dashboard() -> FileResponse:
    base_dir = Path(__file__).resolve().parent
    index_path = base_dir / "static" / "index.html"
    return FileResponse(index_path)
