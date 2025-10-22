from sqlalchemy import Column, Integer, String, Text, BigInteger, Date, Table, ForeignKey
from sqlalchemy.orm import relationship

from core.db.postgres import Base


class Hunter(Base):
    __tablename__ = "hunters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    region = Column(String(255), nullable=False)
    hunt_type = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)


# промежуточная таблица
base_service = Table(
    "base_service",
    Base.metadata,
    Column("base_id", Integer, ForeignKey("hunting_bases.id")),
    Column("service_id", Integer, ForeignKey("services.id"))
)

class HuntingBase(Base):
    __tablename__ = "hunting_bases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    contact_person = Column(String(250), nullable=False)
    contact = Column(String(50), nullable=False)
    website = Column(Text, nullable=True)

    services = relationship("Service", secondary=base_service, back_populates="bases")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)

    bases = relationship("HuntingBase", secondary=base_service, back_populates="services")

