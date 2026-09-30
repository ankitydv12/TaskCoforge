import os
from dataclasses import dataclass
from fastapi import UploadFile
from config import settings

from schemas import upload_progress

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per file
READ_BLOCK = 1024 * 1024          # 1 MB


@dataclass
class UploadResult:
    original_name: str
    saved_path: str | None
    size: int
    ok: bool
    error: str | None = None


async def save_pdf(upload_id:str,files: list[UploadFile]) -> UploadResult:
    """Stream one uploaded PDF to disk. Never raises; failures are returned."""
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    total_files = len(files)
 
    upload_progress[upload_id] = {
        "total": total_files,
        "uploaded": 0,
        "status": "processing"
    }

    for index, file in enumerate(files):
        name = os.path.basename(file.filename or "unnamed.pdf")

        if not name.lower().endswith(".pdf"):
            return UploadResult(name, None, 0, False, "Only .pdf files are allowed")
        
        dest = os.path.join(settings.upload_dir, f"{name}")
        size = 0

        try:
            with open(dest, "wb") as out:
                first = True
                while block := await file.read(READ_BLOCK):
                    if first:
                        if not block.startswith(b"%PDF"):
                            raise ValueError("File content is not a valid PDF")
                        first = False
                    size += len(block)
                    if size > MAX_FILE_SIZE:
                        raise ValueError(f"File exceeds {MAX_FILE_SIZE // (1024 * 1024)} MB limit")
                    out.write(block)
            if size == 0:
                raise ValueError("File is empty")
            upload_progress[upload_id]["uploaded"] = index
        except Exception as exc:
            # Remove partially written file if error occurs
            if os.path.exists(dest):
                os.remove(dest)
            return UploadResult(name, None, size, False, str(exc))
    upload_progress[upload_id]["status"] = "completed"
    return UploadResult(name, dest, size, True)
