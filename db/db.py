from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, text

Base = declarative_base()

class Package(Base):
    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    updated = Column(DateTime, nullable=False)
    created = Column(DateTime, nullable=False, server_default=text('NOW()'))
    max_version = Column(String, nullable=False)
    downloads = Column(Integer, nullable=False)
    description = Column(String)
    repository = Column(String)

class Versions(Base):
    __tablename__ = 'versions'

    id = Column(Integer, primary_key=True)
    version = Column(String, nullable=False)

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
