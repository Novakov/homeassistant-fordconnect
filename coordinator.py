from datetime import timedelta
import json
import logging
from pathlib import Path
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import httpx

from . import const as C
from .model import VehicleData
from .api import FordAPI

LOGGER = logging.getLogger(__name__)  # noqa: F821


class MyDataCoordinatorFromFile(DataUpdateCoordinator[VehicleData]):
    def __init__(self, hass: HomeAssistant, vin: str, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=C.DOMAIN,
            update_interval=timedelta(seconds=15),
            config_entry=entry,
            always_update=True,
        )
        self._vin = vin

    async def _async_update_data(self):
        LOGGER.info("Updating data for VIN: %s", self._vin)

        data = json.loads((Path(__file__).parent / "parsed.json").read_text())

        return data


class MyDataCoordinator(DataUpdateCoordinator[VehicleData]):
    def __init__(
        self, hass: HomeAssistant, session: OAuth2Session, entry: ConfigEntry
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=C.DOMAIN,
            update_interval=timedelta(seconds=30),
            config_entry=entry,
            always_update=True,
        )
        self._session = session
        self.last_update_success = False

    async def _async_update_data(self):
        vin = None
        if self.config_entry:
            vin = self.config_entry.data["vin"]

        LOGGER.info("Updating data for VIN: %s", vin)

        await self._session.async_ensure_token_valid()

        ford_api = FordAPI(self._session.token["access_token"])

        try:
            return await ford_api.get_telemetry()
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 429:
                raise UpdateFailed(retry_after=60) from err
