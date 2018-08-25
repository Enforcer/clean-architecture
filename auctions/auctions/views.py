import json
from decimal import Decimal

import inject
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt

from auctions.application import (
    repositories,
)
from auctions.application.use_cases import placing_bid


def details(request: HttpRequest, auction_id: int) -> HttpResponse:
    repo: repositories.AuctionsRepository = inject.instance(repositories.AuctionsRepository)
    auction = repo.get(auction_id)
    return HttpResponse(escape("Brilliant auction! %s." % auction))


class PlacingBidPresenter(placing_bid.PlacingBidOutputBoundary):
    def present(self, output_dto: placing_bid.PlacingBidOutputDto) -> None:
        self._data = {
            'is_winner': output_dto.is_winner,
            'current_price': round(output_dto.current_price, 2)
        }

    def get_presented_data(self) -> dict:
        return self._data


@csrf_exempt
@login_required
def make_a_bid(request: HttpRequest, auction_id: int) -> HttpResponse:
    data = json.loads(request.body)
    input_dto = placing_bid.PlacingBidInputDto(
        user_id=request.user.id,
        auction_id=auction_id,
        amount=Decimal(data['amount'])
    )
    presenter = PlacingBidPresenter()
    uc = placing_bid.PlacingBidUseCase(presenter)
    uc.execute(input_dto)

    data = presenter.get_presented_data()
    if data['is_winner']:
        return HttpResponse(f'Congratulations! You are a winner! :) Current price is {data["current_price"]}')
    else:
        return HttpResponse(f'Unfortunately, you are not winning. :( Current price is {data["current_price"]}')
