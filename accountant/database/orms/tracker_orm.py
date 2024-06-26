from accountant.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, DECIMAL, String
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class Tracker(AbstractBase):

    __tablename__ = "trackers"
    tracker_uid = Column(UUID, primary_key=True, default=uuid4)
    amount = Column(DECIMAL, nullable=False)
    label = Column(String, nullable=True)
    description = Column(String, nullable=True)
    amount_type = Column(String, nullable=False)
    user_uid = Column(UUID, nullable=False)
