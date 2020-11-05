from dataclasses import dataclass, fields


@dataclass
class Request:
    url = "https://api.stripe.com"
    method = "GET"

    def to_params(self) -> dict:
        """
        Return a dict to a dict.

        Args:
            self: (todo): write your description
        """
        return {field.name: getattr(self, field.name) for field in fields(self) if not field.name.startswith("_")}


@dataclass
class ChargeRequest(Request):
    source: str
    currency: str
    amount: str
    capture: bool = False
    url = f"{Request.url}/v1/charges"
    method = "POST"


@dataclass
class CaptureRequest(Request):
    _capture_id: str
    method = "POST"

    @property
    def url(self) -> str:  # type: ignore
        """
        Returns the url for the url.

        Args:
            self: (todo): write your description
        """
        return f"{Request.url}/v1/charges/{self._capture_id}/capture"
