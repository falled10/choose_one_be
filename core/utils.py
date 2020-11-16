import boto3
import shutil
import random
import string

from fastapi import UploadFile
from humps import camelize

from core.settings import AWS_BUCKET_NAME, DEFAULT_MEDIA_FOLDER, S3_OBJECT_URL


def to_camel(string: str) -> str:
    """Camelize all incoming and returned data from pydantic schemas"""
    return camelize(string)


def generate_unique_filename(filename):
    """Util for generate unique filename
    by adding random ascii symbols to the end of `filename`
    """
    filename, ext = filename.rsplit('.')
    return f"{filename}_{''.join(random.choice(string.ascii_lowercase) for _ in range(6))}.{ext}"


def upload_file(file: UploadFile):
    """Use this util for upload file
    If you are using S3, please make sure that you have set `AWS_BUCKET_NAME`
    after this util checks bucket name it will upload `file` to S3 bucket
    """
    filename = generate_unique_filename(file.filename)
    filepath = DEFAULT_MEDIA_FOLDER + filename
    if AWS_BUCKET_NAME:
        client = boto3.client('s3')
        client.upload_fileobj(file.file, AWS_BUCKET_NAME, filepath)
        return S3_OBJECT_URL + filepath
    with open(filepath, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filepath
