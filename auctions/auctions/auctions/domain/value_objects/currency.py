class Currency:
    decimal_precision = 2
    iso_code = None
    symbol = None


class USD(Currency):
    iso_code = "USD"
    symbol = "$"
