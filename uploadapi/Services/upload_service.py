import os
from dataclasses import dataclass
from fastapi import UploadFile
from Configs.config import settings

from Schemas.schemas import upload_progress

import asyncio

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per file
READ_BLOCK = 1024 * 1024          # 1 MB
CONCURRENT_UPLOADS = 5


@dataclass
class UploadResult:
    original_name: str
    saved_path: str | None
    size: int
    ok: bool
    error: str | None = None

async def save_single_pdf(
        upload_id : str,
        file : UploadFile ,
        index : int ,
        semaphore : asyncio.Semaphore
)-> UploadResult:

    async with semaphore:
        name = os.path.basename(
            file.filename or "unnamed.pdf"
        )

        if not name.lower().endswith(".pdf"):
            return UploadResult(
                name,
                None,
                0,
                False,
                "Only Pdf files are allowed"
            )
        des = os.path.join(settings.upload_dir,name)

        size = 0

        try:
            with open(des,"wb") as out:

                first = True
                while block := await file.read(READ_BLOCK):

                    if first:
                        if not block.startswith(b"%PDF"):
                            raise ValueError(
                                "File not Contain a valid pdf"
                            )
                    first = False

                    size += len(block)

                    if size > MAX_FILE_SIZE:
                        raise ValueError(
                            "File Exceed maximum size limit"
                        )
                    out.write(block)
                if size ==0:
                    raise ValueError("File is empty")

                return UploadResult(
                    name,
                    des,
                    size,
                    True
                )
        except Exception as exc:
            if os.path.exists(des):
                os.remove(des)

            return UploadResult(
                name,
                None,
                size,
                False,
                str(exc)
            )

        finally:

            await file.close()

            upload_progress[upload_id]["uploaded"] += 1




async def save_pdf(
    upload_id: str,
    files: list[UploadFile]
) -> list[UploadResult]:

    print("save_pdf executed:", upload_id)

    os.makedirs(
        settings.upload_dir,
        exist_ok=True
    )

    total_files = len(files)

    upload_progress[upload_id] = {
        "total": total_files,
        "uploaded": 0,
        "status": "processing"
    }

    semaphore = asyncio.Semaphore(
        CONCURRENT_UPLOADS
    )

    tasks = [
        asyncio.create_task(
            save_single_pdf(
                upload_id,
                file,
                index,
                semaphore
            )
        )
        for index, file in enumerate(files, start=1)
    ]

    results = await asyncio.gather(
        *tasks
    )

    upload_progress[upload_id]["status"] = "uploaded"

    return results