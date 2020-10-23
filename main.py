from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from core.exceptions import CustomValidationError
from core.settings import CORS_ORIGINS
from api.auth.routes import router as auth_router
from api.polls.routes import router as poll_router
from api.profile.routes import router as profile_router

app = FastAPI()

app.include_router(auth_router, prefix="/api/auth", tags=["Authorization"])
app.include_router(poll_router, prefix="/api/polls", tags=["Polls"])
app.include_router(profile_router, prefix="/api/profile", tags=['Profile'])


app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({i['loc'][-1]: i['msg'] for i in exc.errors()})
    )


@app.exception_handler(CustomValidationError)
async def validation_custom_exception_handler(request: Request, exc: CustomValidationError):  # noqa
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({exc.field: exc.message})
    )


@app.get('/')
async def main():
    return {'message': 'Hello World!'}
