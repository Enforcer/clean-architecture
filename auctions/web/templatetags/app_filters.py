from decimal import Decimal

from django import template

from auctions.domain.factories import get_dollars


register = template.Library()


@register.filter(name='dollars')
def format_as_dollars(amount: Decimal) -> str:
    return str(get_dollars(amount))


@register.filter(name='anonymize')
def anonymize(str_to_anonymize: str) -> str:
    return str_to_anonymize[0] + '...'
