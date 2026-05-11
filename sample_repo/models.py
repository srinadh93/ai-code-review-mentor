# sample_repo/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)

    # Bug: __init__ is not defined, relying on default that doesn't validate
    # The test test_user_creation_no_email will fail because of this
    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"

    def validate_email(self):
        if "@" not in self.email:
            raise ValueError("Invalid email address")
        return True