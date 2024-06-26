from accountant.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, DECIMAL, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4


class Platform(AbstractBase):
    __tablename__ = "platforms"

    platform_uid = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    login_details = Column(JSONB, nullable=True)
    user_group_uid = Column(
        UUID, ForeignKey("user_group.user_uid", ondelete="CASCADE"), nullable=False
    )


class Investment(AbstractBase):

    __tablename__ = "investment"

    investment_uid = Column(UUID, primary_key=True, default=uuid4)
    return_on_investment = Column(DECIMAL, nullable=False)
    platform_uid = Column(
        UUID, ForeignKey("platforms.platform_uid", ondelete="CASCADE"), nullable=False
    )
    nature = Column(String, nullable=False)
    duration = Column(Date, nullable=False)
    user_group_uid = Column(UUID, nullable=False)
    platform = relationship("Platform")


class InvestmemtTracker(AbstractBase):
    __tablename__ = "investment tracker"

    uid = Column(UUID, primary_key=True, default=uuid4)
    amount = Column(DECIMAL, nullable=False)
    investment_uid = Column(
        UUID,
        ForeignKey("investment.investment_uid", ondelete="CASCADE"),
        nullable=False,
    )
    transaction_type = Column(String, nullable=False)
    investment = relationship("Investment")
