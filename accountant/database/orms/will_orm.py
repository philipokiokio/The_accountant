from sqlalchemy import Column, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from accountant.root.utils.abstract_base import AbstractBase


class Will(AbstractBase):

    __tablename__ = "will"
    will_uid = Column(UUID, primary_key=True, default=uuid4)
    investment_uid = Column(
        UUID,
        ForeignKey("investment.investment_uid", ondelete="CASCADE"),
        nullable=False,
    )
    invitation_uid = Column(
        UUID, ForeignKey("user_group_invitation.uid", ondelete="CASCADE"), nullable=True
    )
    assigned_uid = Column(
        UUID, ForeignKey("users.user_uid", ondelete="CASCADE"), nullable=True
    )
    owner_uid = Column(
        UUID, ForeignKey("users.user_uid", ondelete="CASCADE"), nullable=False
    )
    date_claimed = Column(Date, mullable=True)
    is_claimed = Column(Boolean, server_default=str(False))
    investment = relationship("Investment")
