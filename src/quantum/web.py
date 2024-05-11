from fastapi import FastAPI

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
