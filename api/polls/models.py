from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from api.users.models import User
from core.database import Base
from core.mixins import SearchableMixin


class Poll(SearchableMixin, Base):
    __tablename__ = 'polls'
    __searchable__ = ['title', 'description']
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    slug = Column(String, unique=True)
    creator_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'))
    description = Column(Text, nullable=True, default="")
    media_type = Column(String, default="IMAGE")
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship(User, foreign_keys='Poll.creator_id', back_populates="polls")
    options = relationship("Option", back_populates="poll", passive_deletes=True)
    user_polls = relationship("UserPoll", back_populates="poll", passive_deletes=True)

    @classmethod
    def search(cls, query, page, per_page):
        query = {'multi_match': {'query': query, 'fields': ['*']}}
        return super().search(query, page, per_page)


class Option(Base):
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    label = Column(String)
    media = Column(String, nullable=True)
    poll_id = Column(Integer, ForeignKey(Poll.id, ondelete='CASCADE'))

    poll = relationship("Poll", foreign_keys="Option.poll_id", back_populates="options")
    user_options = relationship("UserOption", back_populates="option")
