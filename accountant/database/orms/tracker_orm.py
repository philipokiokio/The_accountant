from accountant.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, DECIMAL, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class Tracker(AbstractBase):

    __tablename__ = "trackers"
    tracker_uid = Column(UUID, primary_key=True, default=uuid4)
    amount = Column(DECIMAL, nullable=False)
    label = Column(String, nullable=True)
    month = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    currency = Column(String, nullable=False)
    user_uid = Column(UUID, nullable=False)
