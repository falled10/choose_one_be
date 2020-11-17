import boto3
import random
import string

from io import BytesIO
from PIL import Image

from fastapi import UploadFile, HTTPException
from humps import camelize

from core.settings import AWS_BUCKET_NAME, DEFAULT_MEDIA_FOLDER, S3_OBJECT_URL, \
    IMAGE_MAX_WIDTH, AWS_SECRET_KEY, AWS_PUBLIC_KEY


def to_camel(string: str) -> str:
    """Camelize all incoming and returned data from pydantic schemas"""
    return camelize(string)


def generate_unique_filename(filename):
    """Util for generate unique filename
    by adding random ascii symbols to the end of `filename`
    """
    filename, ext = filename.rsplit('.')
    return f"{filename}_{''.join(random.choice(string.ascii_lowercase) for _ in range(6))}.{ext}"


def resize_image(image):
    """Resize image to max width and return it
    """
    try:
        im = Image.open(image)
        w, h = im.size
        if w > IMAGE_MAX_WIDTH:
            new_height = h / w * IMAGE_MAX_WIDTH
            im = im.resize((int(IMAGE_MAX_WIDTH), int(new_height)), Image.ANTIALIAS)
    except OSError as e:
        raise HTTPException(status_code=400, detail=f"Wrong image format. {e}")

    return im


def bytes_from_image(image, img_format='jpeg'):
    """Converts pillow image file to bytes"""
    image = image.convert('RGB')
    with BytesIO() as output:
        image.save(output, format=img_format)
        contents = output.getvalue()
    return contents


def upload_file(file: UploadFile):
    """Use this util for upload file
    If you are using S3, please make sure that you have set `AWS_BUCKET_NAME`
    after this util checks bucket name it will upload `file` to S3 bucket
    """
    filename = generate_unique_filename(file.filename)
    filepath = DEFAULT_MEDIA_FOLDER + filename
    file = bytes_from_image(resize_image(file.file))
    if AWS_BUCKET_NAME:
        client = boto3.client('s3', aws_access_key_id=AWS_PUBLIC_KEY,
                              aws_secret_access_key=AWS_SECRET_KEY)
        client.upload_fileobj(BytesIO(file), AWS_BUCKET_NAME, filepath)
        return S3_OBJECT_URL + filepath
    with open(filepath, 'wb') as buffer:
        buffer.write(file)
    return filepath
