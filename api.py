from typing import TypedDict, cast
from httpx import AsyncClient

from .model import VehicleData, parse_api_response


class Garage(TypedDict):
    vin: str


class FordAPI:
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token
        self._client = AsyncClient(headers={"Authorization": f"Bearer {access_token}"})

    async def get_garage(self) -> Garage:
        r = await self._client.get("https://api.vehicle.ford.com/fcon-query/v1/garage")
        r.raise_for_status()
        return cast(Garage, r.json())

    async def get_telemetry(self) -> VehicleData:
        r = await self._client.get(
            "https://api.vehicle.ford.com/fcon-query/v1/telemetry"
        )
        r.raise_for_status()
        data = r.json()
        return parse_api_response(data)
