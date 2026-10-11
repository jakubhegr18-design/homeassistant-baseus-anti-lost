"""Config flow for the Baseus Anti-Lost T2 integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_EMAIL,
    CONF_ENABLE_LOCATION,
    CONF_MODE,
    CONF_NOTIFY_WHEN_LOST,
    CONF_OUT_OF_RANGE_TIMEOUT,
    CONF_PASSWORD,
    CONF_RSSI_THRESHOLD,
    DEFAULT_ENABLE_LOCATION,
    DEFAULT_NOTIFY_WHEN_LOST,
    DEFAULT_OUT_OF_RANGE_TIMEOUT,
    DEFAULT_RSSI_THRESHOLD,
    DOMAIN,
    MODE_ACCOUNT,
    MODE_BLUETOOTH,
)

_LOGGER = logging.getLogger(__name__)

# Local name prefixes used by Baseus trackers.
NAME_PREFIXES = ("Baseus", "Anti-Lost", "ANTI-LOST", "T2")


class BaseusAntiLostConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Baseus Anti-Lost T2."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered: dict[str, str] = {}
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovery_name: str | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle automatic Bluetooth discovery (triggered by manifest matchers)."""
        _LOGGER.debug("Auto-discovered Baseus device: %s", discovery_info.address)

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured(
            updates={CONF_ADDRESS: discovery_info.address}
        )

        self._discovery_info = discovery_info
        self._discovery_name = discovery_info.name or discovery_info.address
        self.context["title_placeholders"] = {"name": self._discovery_name}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask the user to confirm adding the auto-discovered device."""
        assert self._discovery_info is not None

        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery_name or self._discovery_info.address,
                data={
                    CONF_ADDRESS: self._discovery_info.address,
                    CONF_MODE: MODE_BLUETOOTH,
                },
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": self._discovery_name or self._discovery_info.address
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Let the user choose the setup method manually."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["user_bluetooth", "account"],
        )

    async def async_step_user_bluetooth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Pick a nearby Baseus tracker (or enter its MAC) manually."""
        for info in async_discovered_service_info(self.hass):
            if any(info.name and info.name.startswith(p) for p in NAME_PREFIXES):
                self._discovered[info.address] = info.name or info.address

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._discovered.get(address, address),
                data={CONF_ADDRESS: address, CONF_MODE: MODE_BLUETOOTH},
            )

        if not self._discovered:
            return self.async_show_form(
                step_id="user_bluetooth",
                data_schema=vol.Schema({vol.Required(CONF_ADDRESS): str}),
            )

        return self.async_show_form(
            step_id="user_bluetooth",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(
                        {addr: name for addr, name in self._discovered.items()}
                    )
                }
            ),
        )

    async def async_step_account(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Set up the device through a Baseus account."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input.get("name", address),
                data={
                    CONF_ADDRESS: address,
                    CONF_MODE: MODE_ACCOUNT,
                    CONF_EMAIL: user_input[CONF_EMAIL],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
            )

        return self.async_show_form(
            step_id="account",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default="Anti-Lost T2"): str,
                    vol.Required(CONF_ADDRESS): str,
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "BaseusAntiLostOptionsFlow":
        """Return the options flow."""
        return BaseusAntiLostOptionsFlow()


class BaseusAntiLostOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the Baseus Anti-Lost T2 integration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_RSSI_THRESHOLD,
                        default=options.get(CONF_RSSI_THRESHOLD, DEFAULT_RSSI_THRESHOLD),
                    ): vol.Coerce(int),
                    vol.Optional(
                        CONF_OUT_OF_RANGE_TIMEOUT,
                        default=options.get(
                            CONF_OUT_OF_RANGE_TIMEOUT, DEFAULT_OUT_OF_RANGE_TIMEOUT
                        ),
                    ): vol.Coerce(int),
                    vol.Optional(
                        CONF_NOTIFY_WHEN_LOST,
                        default=options.get(
                            CONF_NOTIFY_WHEN_LOST, DEFAULT_NOTIFY_WHEN_LOST
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_ENABLE_LOCATION,
                        default=options.get(
                            CONF_ENABLE_LOCATION, DEFAULT_ENABLE_LOCATION
                        ),
                    ): bool,
                }
            ),
        )
