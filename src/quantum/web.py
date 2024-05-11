import os.path
from uuid import UUID

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

from quantum import settings
from quantum.entities.web import PingResponse, PrintingTaskWeb, SetTaskPrintingCompleteRequest, TryGetTaskResponse
from quantum.services import printing

app = FastAPI()


@app.get('/ping')
async def ping() -> PingResponse:
    return PingResponse()


@app.get('/try-get-task')
async def try_get_task(
        printer_id: int,  # unused
) -> TryGetTaskResponse:
    return TryGetTaskResponse(
        task=(
            PrintingTaskWeb.from_internal(printing_task)
            if (printing_task := await printing.try_get_next_task(printer_id)) is not None
            else None
        )
    )


@app.post('/set-task-printing-complete/')
async def set_task_printing_complete(
        request: SetTaskPrintingCompleteRequest,
):
    await printing.update_status_then_notify(request.task_id, request.status)


@app.get('/download-file')
async def download_file(
        printing_task_id: UUID,
):
    filename: str = f'{printing_task_id}.pdf'
    filepath: str = f'{settings.FILESTORAGE_PATH}/{filename}'

    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f'File not exists: {filepath}')

    return FileResponse(path=filepath, filename=filename)
