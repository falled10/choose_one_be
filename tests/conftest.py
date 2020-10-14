import pytest

from typing import Generator
from werkzeug.security import generate_password_hash

from sqlalchemy_utils import create_database, database_exists
from alembic.command import upgrade
from alembic.config import Config
from fastapi.testclient import TestClient

from api.users.models import User
from main import app
from core.base import Base
from core.database import engine, SessionLocal
from core.settings import DATABASE_URI

try:
    create_database(engine.url)
except:
    print('database exists')

alembic_config = Config('alembic.ini')
alembic_config.set_main_option('sqlalchemy.url', DATABASE_URI)
upgrade(alembic_config, 'head')


@pytest.fixture()
def db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@pytest.yield_fixture(autouse=True)
def tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture()
def user(db):
    user = User(username='test_user', email='test@mail.com',
                password=generate_password_hash('testpass123', method='sha256'))
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user


@pytest.fixture()
def active_user(db):
    user = User(username='test_user', is_active=True, email='test@mail.com',
                password=generate_password_hash('testpass123', method='sha256'))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
