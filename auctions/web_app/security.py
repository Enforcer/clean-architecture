from typing import Any, Optional

from flask import Flask, request
from flask_security import RoleMixin, Security, UserMixin
from flask_security.datastore import UserDatastore
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session, backref, relationship

from db_infrastructure import Base

__all__ = ["setup", "User"]


class RolesUsers(Base):
    __tablename__ = "roles_users"

    id = Column(Integer, primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    role_id = Column("role_id", Integer, ForeignKey("roles.id"))


class Role(Base, RoleMixin):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship("Role", secondary="roles_users", backref=backref("users", lazy="dynamic"))


class SaUserDatastore(UserDatastore):
    def get_user(self, identifier: Any) -> Optional[User]:
        try:
            email = str(identifier)
        except (ValueError, TypeError):
            return None
        else:
            return self.session.query(User).filter(User.email == email).one_or_none()

    def find_user(self, **kwargs: dict) -> User:
        return self.session.query(User).filter_by(**kwargs).one()

    def put(self, model: User) -> User:
        self.session.add(model)
        return model

    def delete(self, model: User) -> None:
        self.session.delete(model)

    def commit(self) -> None:
        self.session.commit()

    def find_role(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @property
    def session(self) -> Session:
        return request.session


def setup(app: Flask) -> None:
    Security().init_app(app, SaUserDatastore(User, None))
