import pytest
from slugify import slugify

from werkzeug.security import generate_password_hash

from sqlalchemy_utils import create_database
from alembic.command import upgrade
from alembic.config import Config
from fastapi.testclient import TestClient

from api.polls.models import Poll
from api.users.models import User
from api.auth.authorization import get_access_token
from main import app
from core.base import Base
from core.database import engine, SessionLocal
from core.settings import DATABASE_URI

try:
    create_database(engine.url)
except Exception:
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
def client() -> TestClient:
    yield TestClient(app)


@pytest.fixture
def poll(active_user, db):
    title = "new test poll"
    poll = Poll(title=title, description="Something about test poll", slug=slugify(title),
                creator=active_user)
    db.add(poll)
    db.commit()
    db.refresh(poll)
    return poll


@pytest.fixture()
def user(db):
    user = User(username='non_active_user', email='non_active_user@mail.com',
                password=generate_password_hash('testpass123', method='sha256'))
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user


@pytest.fixture()
def token_header(active_user):
    return {'Authorization': f"JWT {get_access_token(active_user)}"}


@pytest.fixture()
def active_user(db):
    user = User(username='active_user', is_active=True, email='active_user@mail.com',
                password=generate_password_hash('testpass123', method='sha256'))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
