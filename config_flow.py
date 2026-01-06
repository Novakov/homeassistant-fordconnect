import logging
from typing import Any
from homeassistant.components.http import URL
from homeassistant.helpers import config_entry_oauth2_flow
from aiohttp import web
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_TOKEN
import secrets

from . import const as C

from .api import FordAPI


LOGGER = logging.getLogger(__name__)


class MyOAuthCallbackView(config_entry_oauth2_flow.OAuth2AuthorizeCallbackView):
    url = "/api/ford-oauth/callback"
    name = "api:ford_oauth:callback"
    requires_auth = False

    async def get(self, request: web.Request):
        hass = request.app["hass"]
        short_state = request.url.query.get("state")

        full_state = (
            hass.data.setdefault(C.DOMAIN, {})
            .setdefault("state_map", {})
            .pop(short_state, None)
        )

        if full_state is None:
            LOGGER.error("State %s not found in state map", short_state)
            raise web.HTTPBadRequest(reason="Invalid state parameter")

        fixed_url = request.url.update_query({"state": full_state})
        fixed_request = request.clone(rel_url=str(fixed_url))
        return await super().get(fixed_request)


class FordConnectConfigFlow(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=C.DOMAIN
):
    DOMAIN = C.DOMAIN
    VERSION = 1

    async def async_oauth_create_entry(self, data):
        access_token = data[CONF_TOKEN][CONF_ACCESS_TOKEN]
        ford_api = FordAPI(access_token)

        garage = await ford_api.get_garage()

        return self.async_create_entry(
            title="Ford Query integration",
            data={**data, "vin": garage["vin"], CONF_NAME: "my-name"},
        )

    @property
    def logger(self) -> logging.Logger:
        return LOGGER

    async def async_step_user(self, user_input=None):
        hass = self.hass

        if "oauth_callback_view_registered" not in hass.data.setdefault(C.DOMAIN, {}):
            hass.http.register_view(MyOAuthCallbackView())
            hass.data[C.DOMAIN]["oauth_callback_view_registered"] = True

        return await super().async_step_user(user_input)

    async def async_generate_authorize_url(self) -> str:
        auth_url = URL(await super().async_generate_authorize_url())

        short = secrets.token_urlsafe(16)

        full_state = auth_url.query["state"]
        redirect_uri = URL(auth_url.query["redirect_uri"]).with_path(
            "/api/ford-oauth/callback"
        )
        modified_url = auth_url.update_query(
            {
                "state": short,
                "redirect_uri": str(redirect_uri),
            }
        )

        self.hass.data.setdefault(C.DOMAIN, {}).setdefault("state_map", {})[short] = (
            full_state
        )

        return str(modified_url)

    async def async_step_reauth(self, entry_data):
        """Perform reauth upon migration of old entries."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauth dialog."""
        reauth_entry = self._get_reauth_entry()
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                description_placeholders={"account": reauth_entry.data["id"]},
                errors={},
            )

        return await self.async_step_pick_implementation(
            user_input={"implementation": reauth_entry.data["auth_implementation"]}
        )
