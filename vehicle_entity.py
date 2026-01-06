from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .coordinator import MyDataCoordinator
from . import const as C


class VehicleEntity(CoordinatorEntity[MyDataCoordinator]):
    def __init__(
        self, coordinator: MyDataCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)

        self._entry = entry

    @property
    def unique_id(self) -> str | None:
        return f"{self.config_entry.entry_id}_{self._attr_name}"

    @property
    def config_entry(self) -> ConfigEntry:
        """Return the config entry."""
        return self._entry

    @property
    def device_info(self) -> DeviceInfo:
        vin = self._entry.data["vin"]
        return DeviceInfo(
            identifiers={(C.DOMAIN, vin)},
            name=f"Vehicle {vin}",
        )
