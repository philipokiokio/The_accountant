from accountant.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, DECIMAL, Date, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4


class Platform(AbstractBase):
    __tablename__ = "platforms"

    platform_uid = Column(UUID, primary_key=True, default=uuid4)
    platform_website = Column(String, nullable=False)
    platform_type = Column(String, nullable=True)
    name = Column(String, nullable=False)
    access_credential = Column(JSONB, nullable=True)
    user_group_uid = Column(
        UUID,
        ForeignKey("user_group.user_group_uid", ondelete="CASCADE"),
        nullable=False,
    )
    investment = relationship("Investment", back_populates="platform")


class Investment(AbstractBase):

    __tablename__ = "investment"

    investment_uid = Column(UUID, primary_key=True, default=uuid4)
    return_on_investment = Column(DECIMAL, nullable=False)
    platform_uid = Column(
        UUID, ForeignKey("platforms.platform_uid", ondelete="CASCADE"), nullable=False
    )
    plan_name = Column(String, nullable=False)
    nature = Column(String, nullable=False)
    end_date = Column(Date, nullable=False)
    is_still_open = Column(Boolean, nullable=False)
    user_group_uid = Column(
        UUID,
        ForeignKey("user_group.user_group_uid", ondelete="CASCADE"),
        nullable=False,
    )
    platform = relationship("Platform")
    trackers = relationship("InvestmentTracker", back_populates="investment")


class InvestmentTracker(AbstractBase):
    __tablename__ = "investment tracker"

    uid = Column(UUID, primary_key=True, default=uuid4)
    amount = Column(DECIMAL, nullable=False)
    currency = Column(String, nullable=False)
    investment_uid = Column(
        UUID,
        ForeignKey("investment.investment_uid", ondelete="CASCADE"),
        nullable=False,
    )
    transaction_type = Column(String, nullable=False)
    investment = relationship("Investment")
