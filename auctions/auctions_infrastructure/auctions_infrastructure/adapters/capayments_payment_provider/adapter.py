from dataclasses import asdict
from typing import Type, TypeVar

import requests

from auctions.domain.types import AuctionId, BidderId
from auctions.domain.value_objects import Money
from auctions.application.ports.payment_provider import PaymentFailedError, PaymentProvider
from auctions_infrastructure.adapters.capayments_payment_provider.requests import ChargeRequest, Request
from auctions_infrastructure.adapters.capayments_payment_provider.responses import ChargeResponse
from auctions_infrastructure.adapters.capayments_payment_provider import dao


ResponseCls = TypeVar("ResponseCls")


class CaPaymentsPaymentProvider(PaymentProvider):
    def __init__(self, login: str, password: str) -> None:
        self.auth = (login, password)

    def pay_for_won_auction(self, auction_id: AuctionId, bidder_id: BidderId, charge: Money) -> None:
        currency = charge.currency.iso_code
        amount = f"{charge.amount:f}"

        request = ChargeRequest(card_token=dao.get_bidders_card_token(bidder_id), currency=currency, amount=amount)
        response = self._execute_request(request, ChargeResponse)

        dao.record_successful_payment(auction_id, bidder_id, charge, charge_uuid=response.charge_uuid)

    def _execute_request(self, request: Request, response_cls: Type[ResponseCls]) -> ResponseCls:
        response = requests.post(request.url, auth=self.auth, json=asdict(request))
        if not response.ok:
            raise PaymentFailedError
        else:
            return response_cls(**response.json())
