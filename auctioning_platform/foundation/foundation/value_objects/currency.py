class Currency:
    decimal_precision = 2
    iso_code = "OVERRIDE"
    symbol = "OVERRIDE"


class USD(Currency):
    iso_code = "USD"
    symbol = "$"
