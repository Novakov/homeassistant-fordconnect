from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.lock import LockEntity

from . import const as C
from .vehicle_entity import VehicleEntity
from .coordinator import MyDataCoordinator


class HoodStatusEntity(VehicleEntity, LockEntity):
    _attr_has_entity_name = True
    _attr_name = "Hood"

    @callback
    def _handle_coordinator_update(self) -> None:
        status = self.coordinator.data["hood_status"]
        self._attr_is_open = status != "CLOSED"
        self.async_write_ha_state()


class AllDoorsEntity(VehicleEntity, LockEntity):
    _attr_has_entity_name = True
    _attr_name = "All Doors"

    @callback
    def _handle_coordinator_update(self) -> None:
        status = self.coordinator.data["doors"]["all_doors_locked"]
        self._attr_is_locked = status
        self.async_write_ha_state()


class DoorEntity(VehicleEntity, LockEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MyDataCoordinator,
        entry: ConfigEntry,
        door: str,
        friendly_name: str,
    ) -> None:
        super().__init__(coordinator, entry)
        self._door = door
        self._attr_name = friendly_name

    @callback
    def _handle_coordinator_update(self) -> None:
        all_locked = self.coordinator.data["doors"]["all_doors_locked"]
        door = self.coordinator.data["doors"][self._door]
        self._attr_is_locked = all_locked
        self._attr_is_open = door["closed"] is False
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = hass.data[C.DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    async_add_entities(
        [
            HoodStatusEntity(coordinator, entry),
            AllDoorsEntity(coordinator, entry),
            DoorEntity(coordinator, entry, "front_left", "Door: Front Left"),
            DoorEntity(coordinator, entry, "front_right", "Door: Front Right"),
            DoorEntity(coordinator, entry, "rear_left", "Door: Rear Left"),
            DoorEntity(coordinator, entry, "rear_right", "Door: Rear Right"),
        ],
        update_before_add=False,
    )
