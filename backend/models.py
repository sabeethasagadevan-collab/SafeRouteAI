from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

def utcnow():
    return datetime.now(timezone.utc)

class RouteHistory(Base):
    __tablename__ = "route_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    start_label: Mapped[str] = mapped_column(String(300), default="")
    destination_label: Mapped[str] = mapped_column(String(300), default="")
    travel_mode: Mapped[str] = mapped_column(String(20), default="car")
    distance_m: Mapped[float] = mapped_column(Float, default=0)
    duration_s: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    data_status: Mapped[str] = mapped_column(String(50), default="partial")

class Observation(Base):
    __tablename__ = "observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    level: Mapped[str] = mapped_column(String(20), default="UNKNOWN")
    source: Mapped[str] = mapped_column(String(100), default="")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    details: Mapped[str] = mapped_column(Text, default="")
