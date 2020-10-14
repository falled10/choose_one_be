from sqlalchemy.orm import Session

from api.polls.models import Poll
from core.exceptions import CustomValidationError


def validate_unique_title(poll: Poll, title: str, db: Session):
    obj = db.query(Poll).filter_by(title=title).first()
    if obj and obj != poll:
        raise CustomValidationError(field="title", message="Poll with this title already exists")
