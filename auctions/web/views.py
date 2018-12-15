import json
from dataclasses import asdict

import dacite
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.template import (
    Context,
    Template,
)
from django.views.decorators.csrf import csrf_exempt

from auctions.application.use_cases import placing_bid
from auctions.domain.factories import get_dollars
from auctions_infrastructure.queries import GetAuctionDetails


def details(request: HttpRequest, auction_id: int) -> HttpResponse:
    try:
        dto = GetAuctionDetails().query(auction_id)
    except ObjectDoesNotExist:
        raise Http404(f'Auction #{auction_id} does not exist!')

    ctx = Context(asdict(dto))
    tpl = Template(
        '''{% load app_filters %}'''
        '''Auction: {{ auction.title }}<br>'''
        '''Price changed from {{ auction.starting_price|dollars }}'''
        '''to {{ auction.current_price|dollars }}<br>'''
        '''Top bids:<br>'''
        '''{% for bid in bids %}'''
        '''{{ bid.amount|dollars }} by {{ bid.bidder.username|anonymize }}<br>'''
        '''{% endfor %}'''
    )
    return HttpResponse(tpl.render(ctx))


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
