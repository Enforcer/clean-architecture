import re

import funcy
from django.contrib import admin

from auctions.application import use_cases
from auctions.models import (
    Auction,
    Bid,
)


class BidInline(admin.TabularInline):
    model = Bid


class AuctionAdmin(admin.ModelAdmin):
    inlines = [BidInline]

    def save_related(self, request, form, formsets, *args, **kwargs):
        ids_of_deleted_bids = self._get_ids_of_deleted_bids(formsets)

        use_case = use_cases.WithdrawingBidsUseCase()
        use_case.withdraw_bids(auction_id=form.instance.pk, bids_ids=ids_of_deleted_bids)

        super().save_related(request, _form, formsets, *args, **kwargs)

    def _get_ids_of_deleted_bids(self, formsets):
        ids = set()
        for form in formsets:
            rows_numbers_for_deletion = set()
            for key in form.data.keys():
                match = re.match(r'bid_set-(\d+)-DELETE', key)
                if match and form.data[key] == 'on':
                    bid_id_key = f'bid_set-{match.group(1)}-id'
                    ids.add(funcy.first(form.data[bid_id_key]))

        return ids



admin.site.register(Auction, AuctionAdmin)
