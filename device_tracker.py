from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.device_tracker import TrackerEntity

from . import const as C
from .vehicle_entity import VehicleEntity


class PositionEntity(VehicleEntity, TrackerEntity):
    _attr_has_entity_name = True
    _attr_name = "Vehicle Position"

    @callback
    def _handle_coordinator_update(self) -> None:
        _, lat, long, alt = self.coordinator.data["position"]
        self._attr_latitude = lat
        self._attr_longitude = long
        self._attr_altitude = alt
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
            PositionEntity(coordinator, entry),
        ],
        update_before_add=False,
    )
