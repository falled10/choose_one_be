from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from api.users.models import User
from api.polls.models import Poll, Option
from core.database import Base


class UserPoll(Base):
    __tablename__ = 'user_polls'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    poll_id = Column(Integer, ForeignKey(Poll.id, ondelete='CASCADE'))

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(User, foreign_keys='UserPoll.user_id', back_populates="user_polls")
    poll = relationship(Poll, foreign_keys='UserPoll.poll_id', back_populates="user_polls")
    user_options = relationship("UserOption", back_populates="poll", passive_deletes=True)


class UserOption(Base):
    __tablename__ = 'user_options'
    id = Column(Integer, primary_key=True)
    place_number = Column(Integer)
    poll_id = Column(Integer, ForeignKey(UserPoll.id, ondelete='CASCADE'))
    option_id = Column(Integer, ForeignKey(Option.id, ondelete='CASCADE'))

    poll = relationship(UserPoll, foreign_keys="UserOption.poll_id", back_populates="user_options")
    option = relationship(Option, foreign_keys="UserOption.option_id", back_populates="user_options")
