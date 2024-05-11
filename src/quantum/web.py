from fastapi import FastAPI

from quantum.entities.web import PingResponse

app = FastAPI()


@app.get('/ping')
async def ping():
    return PingResponse()
