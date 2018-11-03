import json

import dacite
import inject
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt

from auctions.application import repositories
from auctions.application.use_cases import placing_bid
from auctions.domain.factories import get_dollars


def details(request: HttpRequest, auction_id: int) -> HttpResponse:
    repo: repositories.AuctionsRepository = inject.instance(repositories.AuctionsRepository)
    auction = repo.get(auction_id)
    return HttpResponse(escape("Brilliant auction! %s." % auction))


class PlacingBidPresenter(placing_bid.PlacingBidOutputBoundary):
    def present(self, output_dto: placing_bid.PlacingBidOutputDto) -> None:
        # in a textbook example of the Clean Architecture this method would cause HttpResponse to be sent to a client.
        # However, we are in Django.
        self._data = {
            'is_winner': output_dto.is_winner,
            'current_price': str(output_dto.current_price)
        }

    def get_http_response(self) -> HttpResponse:
        if self._data['is_winner']:
            return HttpResponse(
                f'Congratulations! You are a winner! :) Current price is {self._data["current_price"]}'
            )
        else:
            return HttpResponse(
                f'Unfortunately, you are not winning. :( Current price is {self._data["current_price"]}'
            )


@csrf_exempt
@login_required
def make_a_bid(request: HttpRequest, auction_id: int) -> HttpResponse:
    data = json.loads(request.body)
    input_dto = dacite.from_dict(placing_bid.PlacingBidInputDto, {
        'bidder_id': request.user.id,
        'auction_id': auction_id,
        'amount': get_dollars(data['amount'])
    })
    presenter = PlacingBidPresenter()
    uc = placing_bid.PlacingBid(presenter)
    uc.execute(input_dto)

    return presenter.get_http_response()
