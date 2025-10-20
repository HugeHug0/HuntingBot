from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Hunter(Base):
    __tablename__ = "hunters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    region = Column(String(255), nullable=False)
    hunt_type = Column(String(255), nullable=False)


class HuntingBase(Base):
    __tablename__ = "hunting_bases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    tg_username = Column(String(250), nullable=False)
    phone = Column(String(50), nullable=False)
    website = Column(Text(1000), nullable=True)
