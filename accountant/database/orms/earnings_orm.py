from accountant.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, DECIMAL, Date, String
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class Earning(AbstractBase):

    __tablename__ = "earnings"
    earning_uid = Column(UUID, primary_key=True, default=uuid4)
    amount = Column(DECIMAL, nullable=False)
    month = Column(String, nullable=False)
    pay_date = Column(Date, nullable=False)
    user_uid = Column(UUID, nullable=False)
