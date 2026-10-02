import os
from dataclasses import dataclass
from fastapi import UploadFile
from Configs.config import settings

from Schemas.schemas import upload_progress

import asyncio

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per file
READ_BLOCK = 1024 * 1024          # 1 MB


@dataclass
class UploadResult:
    original_name: str
    saved_path: str | None
    size: int
    ok: bool
    error: str | None = None


async def save_pdf(upload_id:str,files: list[UploadFile]) -> list[UploadResult]:
    """Stream one uploaded PDF to disk. Never raises; failures are returned."""
    print("save_pdf executed",upload_id)
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    total_files = len(files)
 
    upload_progress[upload_id] = {
        "total": total_files,
        "uploaded": 0,
        "status": "processing"
    }
    results: list[UploadResult] = []

    for index, file in enumerate(files,start=1):
        #TODO: sleep is for testing purpose 
        await asyncio.sleep(5)
        name = os.path.basename(file.filename or "unnamed.pdf")

        if not name.lower().endswith(".pdf"):
            UploadResult(name, None, 0, False, "Only .pdf files are allowed")
            continue
        
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
                    out.write(block)
            print(size)
            if size == 0:
                raise ValueError("File is empty")
            results.append(
                UploadResult(
                    name,
                    dest,
                    size,
                    True
                )
            )
        finally:
            upload_progress[upload_id]["uploaded"] = index
            await file.close()

    upload_progress[upload_id]["status"] = "uploaded"
    return results
