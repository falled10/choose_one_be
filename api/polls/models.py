from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text

from api.users.models import User
from core.database import Base


class Poll(Base):
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    slug = Column(String, unique=True)
    creator = Column(Integer, ForeignKey(User.id))
    description = Column(Text, nullable=True, default="")
    media_type = Column(String, default="IMAGE")
    places_number = Column(Integer, default=0)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
