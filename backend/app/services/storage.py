from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import Settings


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def media_type_for_filename(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported file extension: {suffix or '<none>'}.",
    )


def safe_upload_name(original_filename: str) -> str:
    suffix = Path(original_filename).suffix.lower()
    return f"{uuid4().hex}{suffix}"


async def save_upload(file: UploadFile, settings: Settings) -> tuple[Path, str]:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename.")

    media_type_for_filename(file.filename)
    stored_filename = safe_upload_name(file.filename)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = settings.upload_dir / stored_filename

    bytes_written = 0
    with target_path.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            bytes_written += len(chunk)
            if bytes_written > settings.max_upload_bytes:
                target_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Upload exceeds {settings.max_upload_mb} MB limit.",
                )
            output.write(chunk)

    return target_path, stored_filename

