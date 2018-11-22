from dataclasses import dataclass

@dataclass
class ChargeResponse:
    success: bool
    charge_uuid: str
