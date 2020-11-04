import pytest

from api.auth.utils import generate_token
from api.profile.validators import validate_forget_password_token
from core.exceptions import CustomValidationError


def test_validate_forget_password_token(user, db):
    token = generate_token(user.email, 'forget_password')
    validated_user = validate_forget_password_token(token, db)
    assert user.id == validated_user.id


def test_validate_forget_password_token_wrong_token_type(user, db):
    token = generate_token(user.email, 'some other type')
    with pytest.raises(CustomValidationError):
        validate_forget_password_token(token, db)


def test_validate_forget_password_token_wrong_token(db):
    with pytest.raises(CustomValidationError):
        validate_forget_password_token('asdfdsafadsfdsa', db)


def test_validate_forget_password_token_wrong_email(db):
    token = generate_token('non_existed@mail.com', 'forget_password')
    with pytest.raises(CustomValidationError):
        validate_forget_password_token(token, db)
