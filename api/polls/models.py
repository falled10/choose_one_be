from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from api.users.models import User
from core.database import Base


class Poll(Base):
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    slug = Column(String, unique=True)
    creator_id = Column(Integer, ForeignKey(User.id))
    description = Column(Text, nullable=True, default="")
    media_type = Column(String, default="IMAGE")
    places_number = Column(Integer, default=0)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship(User, foreign_keys='Poll.creator_id', back_populates="polls")
