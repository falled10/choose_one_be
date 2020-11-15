import boto3
import shutil

from fastapi import UploadFile
from humps import camelize

from core.settings import AWS_BUCKET_NAME, DEFAULT_MEDIA_FOLDER, \
    DEFAULT_MEDIA_FOLDER_URL, S3_OBJECT_URL


def to_camel(string: str) -> str:
    """Camelize all incoming and returned data from pydantic schemas"""
    return camelize(string)


def upload_file(file: UploadFile):
    filepath = DEFAULT_MEDIA_FOLDER + file.filename
    if AWS_BUCKET_NAME:
        client = boto3.client('s3')
        client.upload_fileobj(file.file, AWS_BUCKET_NAME, filepath)
        return S3_OBJECT_URL + file.filename
    with open(filepath, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    return DEFAULT_MEDIA_FOLDER_URL + file.filename
