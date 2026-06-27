from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.restore_state import RestoreEntity

from . import const as C
from .vehicle_entity import VehicleEntity


class PositionEntity(VehicleEntity, TrackerEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Vehicle Position"

    @callback
    def _handle_coordinator_update(self) -> None:
        _, lat, long, alt = self.coordinator.data["position"]
        self._attr_latitude = lat
        self._attr_longitude = long
        self._attr_altitude = alt
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        await super().async_added_to_hass()

        # Restore last state if coordinator hasn't successfully updated yet
        last_state = await self.async_get_last_state()

        if self.coordinator.last_update_success:
            return

        if last_state:
            self._attr_latitude = last_state.attributes.get("latitude")
            self._attr_longitude = last_state.attributes.get("longitude")
            self._attr_altitude = last_state.attributes.get("altitude")

    @property
    def available(self) -> bool:
        return super().available or (
            self._attr_latitude is not None and self._attr_longitude is not None
        )


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
