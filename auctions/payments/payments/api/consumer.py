import dataclasses
from typing import Type, TypeVar

import requests

from payments.api.exceptions import PaymentFailedError
from payments.api.requests import Request

ResponseCls = TypeVar("ResponseCls")


class ApiConsumer:
    def __init__(self, login: str, password: str) -> None:
        self.auth = login, password  # basic auth

    def _execute_request(self, request: Request, response_cls: Type[ResponseCls]) -> ResponseCls:
        response = requests.post(request.url, auth=self.auth, json=dataclasses.asdict(request))
        if not response.ok:
            raise PaymentFailedError
        else:
            return response_cls(**response.json())  # type: ignore
