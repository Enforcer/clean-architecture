from typing import Any, Optional

import inject

from flask import Flask
from flask_security import Security, UserMixin, RoleMixin
from flask_security.datastore import UserDatastore
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship, backref

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
            return inject.instance(Session).query(User).filter(User.email == email).one_or_none()

    def find_user(self, **kwargs: dict) -> User:
        return inject.instance(Session).query(User).filter_by(**kwargs).one()

    def put(self, model: User) -> User:
        inject.instance(Session).add(model)
        return model

    def delete(self, model: User) -> None:
        inject.instance(Session).delete(model)

    def commit(self) -> None:
        inject.instance(Session).commit()

    def find_role(self, *args, **kwargs) -> None:
        raise NotImplementedError


def setup(app: Flask) -> None:
    Security().init_app(app, SaUserDatastore(User, None))
