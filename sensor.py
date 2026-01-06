import logging
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
)

from . import const as C
from .vehicle_entity import VehicleEntity
from .coordinator import MyDataCoordinator


LOGGER = logging.getLogger(__name__)  # noqa: F821


class AmbientTempEntity(VehicleEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Ambient Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = "°C"
    _attr_suggested_display_precision = 1

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["ambient_temp"]
        self.async_write_ha_state()


class BatteryChargeLevelEntity(VehicleEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Battery Charge Level"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = "%"
    _attr_suggested_display_precision = 1

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["battery_charge_level"]
        self.async_write_ha_state()


class BatteryVoltageEntity(VehicleEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Battery Voltage"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = "V"
    _attr_suggested_display_precision = 2

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["battery_voltage"]
        self.async_write_ha_state()


class OdometerEntity(VehicleEntity, RestoreSensor):
    _attr_has_entity_name = True
    _attr_name = "Odometer"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = "km"
    _attr_suggested_display_precision = 0

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["odometer"]
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_sensor_data()

        if self.coordinator.last_update_success:
            return

        if last_state and last_state.native_value:
            self._attr_native_value = last_state.native_value

    @property
    def available(self) -> bool:
        return super().available or self._attr_native_value is not None


class FuelLevelEntity(VehicleEntity, RestoreSensor):
    _attr_has_entity_name = True
    _attr_name = "Fuel Level"
    _attr_device_class = None
    _attr_native_unit_of_measurement = "%"
    _attr_suggested_display_precision = 0
    _attr_state_class = SensorStateClass.MEASUREMENT

    @callback
    def _handle_coordinator_update(self) -> None:
        if (
            self.coordinator.data["fuel_range"] > 0.0
            or self.coordinator.data["ignition_status"] == "ON"
        ):
            self._attr_native_value = self.coordinator.data["fuel_level"]
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_sensor_data()

        if self.coordinator.last_update_success:
            return

        if last_state and last_state.native_value:
            self._attr_native_value = last_state.native_value

    @property
    def available(self) -> bool:
        return super().available or self._attr_native_value is not None


class FuelRangeEntity(VehicleEntity, RestoreSensor):
    _attr_has_entity_name = True
    _attr_name = "Fuel Range"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = "km"
    _attr_suggested_display_precision = 1
    _attr_state_class = SensorStateClass.MEASUREMENT

    @callback
    def _handle_coordinator_update(self) -> None:
        if (
            self.coordinator.data["fuel_range"] > 0.0
            or self.coordinator.data["ignition_status"] == "ON"
        ):
            self._attr_native_value = self.coordinator.data["fuel_range"]
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_sensor_data()

        if self.coordinator.last_update_success:
            return

        if last_state and last_state.native_value:
            self._attr_native_value = last_state.native_value

    @property
    def available(self) -> bool:
        return super().available or self._attr_native_value is not None


class OutsideTemperatureEntity(VehicleEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Outside Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = "°C"
    _attr_suggested_display_precision = 1

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["outside_temperature"]
        self.async_write_ha_state()


class GearLeverPositionEntity(VehicleEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Gear Lever Position"
    _attr_device_class = None
    _attr_native_unit_of_measurement = None

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data[
            "gear_lever_position"
        ].capitalize()
        self.async_write_ha_state()


class IgnitionStatusEntity(VehicleEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Ignition Status"
    _attr_device_class = None
    _attr_native_unit_of_measurement = None

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["ignition_status"].capitalize()
        self.async_write_ha_state()


class TirePressureEntity(VehicleEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.PRESSURE
    _attr_native_unit_of_measurement = "bar"
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: MyDataCoordinator,
        entry: ConfigEntry,
        tire: str,
        friendly_name: str,
    ) -> None:
        super().__init__(coordinator, entry)
        self._tire = tire
        self._attr_name = friendly_name

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["tires"][self._tire]["pressure"]
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
            AmbientTempEntity(coordinator, entry),
            BatteryChargeLevelEntity(coordinator, entry),
            BatteryVoltageEntity(coordinator, entry),
            FuelLevelEntity(coordinator, entry),
            FuelRangeEntity(coordinator, entry),
            OdometerEntity(coordinator, entry),
            OutsideTemperatureEntity(coordinator, entry),
            GearLeverPositionEntity(coordinator, entry),
            IgnitionStatusEntity(coordinator, entry),
            TirePressureEntity(
                coordinator, entry, "front_left", "Tire Pressure: Front Left"
            ),
            TirePressureEntity(
                coordinator, entry, "front_right", "Tire Pressure: Front Right"
            ),
            TirePressureEntity(
                coordinator, entry, "rear_left", "Tire Pressure: Rear Left"
            ),
            TirePressureEntity(
                coordinator, entry, "rear_right", "Tire Pressure: Rear Right"
            ),
        ],
        update_before_add=False,
    )
