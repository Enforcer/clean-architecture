from django.conf import settings
from django.db import models


class Auction(models.Model):
    title = models.CharField(max_length=255)
    starting_price = models.DecimalField(decimal_places=2, max_digits=10)
    current_price = models.DecimalField(decimal_places=2, max_digits=10)
    ends_at = models.DateTimeField()

    def __str__(self):
        return self.title


class Bid(models.Model):
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.bidder} with {self.amount}'


class BidderCardDetails(models.Model):
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    card_token = models.CharField(max_length=255)


class PaymentHistoryEntry(models.Model):
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    auction = models.ForeignKey(Auction, on_delete=models.PROTECT)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    currency = models.CharField(max_length=3)
    charge_uuid = models.UUIDField()
