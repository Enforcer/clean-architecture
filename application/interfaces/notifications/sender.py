from abc import (
    ABCMeta,
    abstractmethod,
)

from .notification import Notification


class NotificationsSender(metaclass=ABCMeta):

    @abstractmethod
    def send(self, notification: Notification):
        pass
