from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    pushplus_token = Column(String(100), nullable=True)
    balance_threshold = Column(Float, default=50.0)
    water_balance_threshold = Column(Float, default=30.0)  # 水费提醒阈值
    created_at = Column(DateTime, default=datetime.now)

    credential = relationship("Credential", back_populates="user", uselist=False)
    crawl_records = relationship("CrawlRecord", back_populates="user")


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    pms_account = Column(String(100), nullable=False)
    pms_password_encrypted = Column(String(255), nullable=False)
    room_info = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="credential")


class CrawlRecord(Base):
    __tablename__ = "crawl_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 电费数据
    balance = Column(Float, nullable=True)
    details_data = Column(Text, nullable=True)
    energy_data = Column(Text, nullable=True)

    # 水费数据
    water_balance = Column(Float, nullable=True)
    water_details_data = Column(Text, nullable=True)
    water_energy_data = Column(Text, nullable=True)

    crawled_at = Column(DateTime, default=datetime.now)
    is_cached = Column(Integer, default=0)  # 0=用户请求, 1=定时任务缓存

    user = relationship("User", back_populates="crawl_records")
