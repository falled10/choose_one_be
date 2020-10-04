from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from core.settings import TORTOISE_CONFIG
from core.exceptions import CustomValidationError
from api.auth.routes import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/api/auth", tags=["authorization"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({i['loc'][-1]: i['msg'] for i in exc.errors()})
    )


@app.exception_handler(CustomValidationError)
async def validation_exception_handler(request: Request, exc: CustomValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({exc.field: exc.message})
    )


@app.get('/')
async def main():
    return {'message': 'Hello World!'}


register_tortoise(
    app,
    config=TORTOISE_CONFIG
)
