import os

import boto3

from moto import mock_s3

from core.settings import ROOT_DIR, AWS_BUCKET_NAME


@mock_s3
def test_upload_new_file(client):
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket=AWS_BUCKET_NAME)
    with open(os.path.join(ROOT_DIR, 'tests/testdata/image.png'), 'rb') as f:
        file = f.read()
    resp = client.post('/upload_file', files={'file': ('testfile.png', file, 'image/png')})
    assert resp.status_code == 201
    assert resp.json()['url']


def test_upload_wrong_file_data(client):
    with open(os.path.join(ROOT_DIR, 'tests/testdata/not_image.png'), 'rb') as f:
        file = f.read()
    resp = client.post('/upload_file', files={'file': ('testfile.png', file, 'image/png')})
    assert resp.status_code == 400
