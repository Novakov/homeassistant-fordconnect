import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.config_entry_oauth2_flow import (
    ImplementationUnavailableError,
    OAuth2Session,
    async_get_config_entry_implementation,
)
import voluptuous as vol

from . import const as C
from .const import DOMAIN
from .coordinator import MyDataCoordinator

_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = vol.Schema({C.DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    try:
        implementation = await async_get_config_entry_implementation(hass, entry)
    except ImplementationUnavailableError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="oauth2_implementation_unavailable",
        ) from err

    _LOGGER.info("Setting up FordConnect entry with data: %s", str(entry.data))
    session = OAuth2Session(hass, entry, implementation)
    vin = entry.data[C.VIN]

    coordinator = MyDataCoordinator(hass, session, entry)

    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "vin": vin,
    }

    await hass.config_entries.async_forward_entry_setups(
        entry,
        [
            "sensor",
            "lock",
            "device_tracker",
        ],
    )
    return True
