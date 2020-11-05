from typing import Any, Optional

from flask import Flask, request
from flask_security import Security
from flask_security.datastore import UserDatastore
from sqlalchemy.orm import Session

from web_app_models import User

__all__ = ["setup", "User"]


class SaUserDatastore(UserDatastore):
    def get_user(self, identifier: Any) -> Optional[User]:
        """
        Get a single user with the given identifier.

        Args:
            self: (todo): write your description
            identifier: (todo): write your description
        """
        try:
            email = str(identifier)
        except (ValueError, TypeError):
            return None
        else:
            return self.session.query(User).filter(User.email == email).one_or_none()

    def find_user(self, **kwargs: dict) -> User:
        """
        Get a user.

        Args:
            self: (todo): write your description
        """
        return self.session.query(User).filter_by(**kwargs).one()

    def put(self, model: User) -> User:
        """
        Put the given model.

        Args:
            self: (todo): write your description
            model: (todo): write your description
        """
        self.session.add(model)
        return model

    def delete(self, model: User) -> None:
        """
        Deletes the given model.

        Args:
            self: (todo): write your description
            model: (todo): write your description
        """
        self.session.delete(model)

    def commit(self) -> None:
        """
        Commit the current transaction.

        Args:
            self: (todo): write your description
        """
        self.session.commit()

    def find_role(self, *args, **kwargs) -> None:  # type: ignore
        """
        Find a single role.

        Args:
            self: (todo): write your description
        """
        raise NotImplementedError

    @property
    def session(self) -> Session:
        """
        Returns the session object.

        Args:
            self: (todo): write your description
        """
        return request.session  # type: ignore


def setup(app: Flask) -> None:
    """
    Flask application.

    Args:
        app: (todo): write your description
    """
    Security().init_app(app, SaUserDatastore(User, None))
