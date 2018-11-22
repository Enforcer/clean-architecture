from dataclasses import dataclass


@dataclass
class Request:
    url = 'http://ca-payments.com:5000/api/v1/'
    method = 'GET'


@dataclass
class ChargeRequest(Request):
    card_token: str
    currency: str
    amount: str
    url = Request.url + 'charge'
    method = 'POST'
