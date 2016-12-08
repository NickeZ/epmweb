from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, text, UniqueConstraint

Base = declarative_base()

class Package(Base):
    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, unique=True, nullable=False)
    updated = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    max_version = Column(String, nullable=False)
    downloads = Column(Integer, nullable=False, default=0)
    description = Column(String)
    repository = Column(String)

    def __repr__(self):
        return '<Package(name={}, updated={}, created={}, max_version={}, downloads={})'.format(
            self.name, self.updated, self.created, self.max_version, self.downloads
        )

class Version(Base):
    __tablename__ = 'versions'

    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    version = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('package_id', 'version'),)

    def __repr__(self):
        return '<Version(package_id={}, version={})'.format(
            self.package_id, self.version
        )

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return '<User(email={})'.format(
            self.email
        )
