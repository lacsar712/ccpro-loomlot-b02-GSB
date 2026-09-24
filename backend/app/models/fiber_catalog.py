from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FiberCatalog(Base):
    """全场纤维名录：染缸纤维只能取自启用项，缸容不得超出名录上限。"""

    __tablename__ = "fiber_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fiber_name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    max_capacity_l: Mapped[float] = mapped_column(Float, nullable=False)
