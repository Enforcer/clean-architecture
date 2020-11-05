import abc

from shipping.domain.entities import Address
from shipping.domain.value_objects import ConsigneeId


class AddressRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, consignee_id: ConsigneeId) -> Address:
        """
        Get a preignee id.

        Args:
            self: (todo): write your description
            consignee_id: (str): write your description
        """
        pass
