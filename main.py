from fastapi import FastAPI, Request, status, UploadFile, File
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.exceptions import CustomValidationError
from core.settings import CORS_ORIGINS
from core.search import es
from core.utils import upload_file
from api.auth.routes import router as auth_router
from api.polls.routes import router as poll_router
from api.profile.routes import router as profile_router
from api.user_polls.routes import router as user_polls_router

app = FastAPI()

app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth_router, prefix="/api/auth", tags=["Authorization"])
app.include_router(poll_router, prefix="/api/polls", tags=["Polls"])
app.include_router(profile_router, prefix="/api/profile", tags=['Profile'])
app.include_router(user_polls_router, prefix="/api/user-polls", tags=['User Polls'])


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


@app.post('/upload_file', status_code=status.HTTP_201_CREATED)
async def upload_file_route(file: UploadFile = File(...)):
    filename = upload_file(file)
    return {'url': filename}


@app.on_event('shutdown')
async def shutdown_event():
    es.close()
