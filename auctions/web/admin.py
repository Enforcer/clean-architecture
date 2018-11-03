import re
import typing

import dacite
import funcy
from django.contrib import admin

from auctions.application.use_cases import withdrawing_bids
from web.models import (
    Auction,
    Bid,
)


class BidInline(admin.TabularInline):
    model = Bid
    readonly_fields = ('amount', 'bidder')

    def has_add_permission(self, request):
        return False


class AuctionAdmin(admin.ModelAdmin):
    inlines = [BidInline]
    readonly_fields = 'current_price',

    def save_related(self, request, form, formsets, *args, **kwargs):
        ids_of_deleted_bids = self._get_ids_of_deleted_bids(formsets)

        use_case = withdrawing_bids.WithdrawingBids()
        input_dto = dacite.from_dict(
            withdrawing_bids.WithdrawingBidsInputDto,
            {'auction_id': form.instance.pk, 'bids_ids': ids_of_deleted_bids}
        )
        use_case.execute(input_dto)

        for formset in formsets:
            formset.new_objects = formset.changed_objects = formset.deleted_objects = []

    def save_model(self, request, obj, form, change):
        obj.save(update_fields=['title', 'starting_price'])

    def _get_ids_of_deleted_bids(self, formsets) -> typing.List[int]:
        ids = set()
        for form in formsets:
            for key in form.data.keys():
                match = re.match(r'bid_set-(\d+)-DELETE', key)
                if match and form.data[key] == 'on':
                    bid_id_key = f'bid_set-{match.group(1)}-id'
                    ids.add(int(funcy.first(form.data[bid_id_key])))

        return list(ids)


admin.site.register(Auction, AuctionAdmin)
