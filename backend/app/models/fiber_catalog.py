from sqlalchemy import String, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FiberCatalog(Base):
    """全场纤维名录：染缸纤维只能引用启用项，缸容受 capacity_limit_l 管束。"""

    __tablename__ = "fiber_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # 该纤维允许的单缸最大容量（升）；建缸/改缸容量不得大于此值
    capacity_limit_l: Mapped[float] = mapped_column(Float, nullable=False)
