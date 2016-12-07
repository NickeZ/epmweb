from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

Base = declarative_base()

class Package(Base):
    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    updated = Column(DateTime)
    created = Column(DateTime)
    downloads = Column(Integer)
    description = Column(String)
    repository = Column(String)
