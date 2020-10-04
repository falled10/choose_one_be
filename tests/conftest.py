import pytest

from typing import Generator

from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.test import initializer, finalizer
from fastapi.testclient import TestClient

from api.users.models import User
from core.settings import TORTOISE_MODELS_LIST
from main import app


@pytest.yield_fixture(autouse=True)
def initialize_tests(request):
    register_tortoise(
        app,
        db_url="sqlite://:memory:",
        modules={"models": TORTOISE_MODELS_LIST},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    initializer(TORTOISE_MODELS_LIST)
    request.addfinalizer(finalizer)


@pytest.fixture(scope="session")
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture()
async def user():
    yield await User.create(username='test_user',
                            email='test@mail.com', password='testpass123')
