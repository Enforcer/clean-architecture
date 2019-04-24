import dataclasses
from typing import Type, TypeVar

import requests

from payments.config import PaymentsConfig
from payments.exceptions import PaymentFailedError
from payments.requests import Request

ResponseCls = TypeVar("ResponseCls")


class PaymentsFacade:
    def __init__(self, config: PaymentsConfig) -> None:
        self.auth = config.login, config.password

    def _execute_request(self, request: Request, response_cls: Type[ResponseCls]) -> ResponseCls:
        response = requests.post(request.url, auth=self.auth, json=dataclasses.asdict(request))
        if not response.ok:
            raise PaymentFailedError
        else:
            return response_cls(**response.json())  # type: ignore

    def trigger_payment(self, auction_id, bidder_id, charge) -> None:
        # moze dostac event AuctionWon i musi zostac przepakowany na cos innego
        # moze rzucic event PaymentSuccessful i powinno isc do Sagi
        # moze rzucic event PaymentFailed i to tez powinno isc do Sagi, ktora odpowiednio zareaguje
        """
        To teraz tak:
         1. Zapisz payment w DB, z jakims statusem
         2. Pusc taska w tlo ktory wykona zadanie i zupdate'uje, ewentualnie pusci kolejny event do Sagi
        """
        pass
        # currency = charge.currency.iso_code
        # amount = f"{charge.amount:f}"
        #
        # request = ChargeRequest(card_token=dao.get_bidders_card_token(bidder_id), currency=currency, amount=amount)
        # response = self._execute_request(request, ChargeResponse)
        #
        # dao.record_successful_payment(auction_id, bidder_id, charge, charge_uuid=response.charge_uuid)
