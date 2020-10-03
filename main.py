from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from core.settings import TORTOISE_CONFIG
from core.logger import project_logger

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({i['loc'][-1]: i['msg'] for i in exc.errors()})
    )


@app.get('/')
async def main():
    project_logger.info("Something very important")
    return {'message': 'Hello World!'}


register_tortoise(
    app,
    config=TORTOISE_CONFIG
)
