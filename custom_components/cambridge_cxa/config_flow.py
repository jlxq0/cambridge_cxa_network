"""Config flow for Cambridge CXA integration."""
import socket
import serial
import serial.tools.list_ports
import voluptuous as vol
import asyncio
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SERIAL_PORT,
    CONF_CONNECTION_TYPE,
    CONF_TCP_HOST,
    CONF_TCP_PORT,
    CONF_SERIAL_PORT,
    CONF_AMP_TYPE,
    CONF_CXN_IP,
    CONNECTION_TCP,
    CONNECTION_SERIAL,
    AMP_TYPES,
)

class CambridgeCXAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cambridge CXA."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.config = {}
        self.connection_type = None

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # User made a selection, proceed to next step
            self.connection_type = user_input[CONF_CONNECTION_TYPE]

            if self.connection_type == CONNECTION_TCP:
                # Go to network configuration
                return await self.async_step_tcp()
            else:
                # Go to serial configuration
                return await self.async_step_serial()

        # Show connection type selection
        schema = vol.Schema({
            vol.Required(CONF_CONNECTION_TYPE): vol.In({
                CONNECTION_TCP: "Network (TCP/IP via USR-W610)",
                CONNECTION_SERIAL: "Serial (USB/RS232)"
            })
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

    async def async_step_tcp(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle TCP configuration."""
        errors = {}

        if user_input is not None:
            # Test if we can connect to the specified IP:port
            valid = await self._test_tcp_connection(
                user_input[CONF_TCP_HOST],
                user_input[CONF_TCP_PORT]
            )

            if valid:
                # Connection successful, save and continue
                self.config = user_input
                self.config[CONF_CONNECTION_TYPE] = CONNECTION_TCP
                return await self.async_step_amp_config()
            else:
                # Connection failed, show error
                errors["base"] = "cannot_connect"

        # Show TCP configuration form
        schema = vol.Schema({
            vol.Required(CONF_TCP_HOST): str,
            vol.Required(CONF_TCP_PORT, default=DEFAULT_PORT): int,
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        })

        return self.async_show_form(
            step_id="tcp",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "Enter the IP address of your USR-W610 device"
            }
        )

    async def async_step_serial(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle serial configuration."""
        errors = {}

        if user_input is not None:
            # Test if we can open the serial port
            valid = await self._test_serial_connection(
                user_input[CONF_SERIAL_PORT]
            )

            if valid:
                # Port opened successfully, continue
                self.config = user_input
                self.config[CONF_CONNECTION_TYPE] = CONNECTION_SERIAL
                return await self.async_step_amp_config()
            else:
                errors["base"] = "cannot_connect"

        # Get list of serial ports on the system
        ports = await self.hass.async_add_executor_job(self._get_serial_ports)

        if not ports:
            # No ports found, allow manual entry
            ports = {DEFAULT_SERIAL_PORT: "No ports detected - enter manually"}

        schema = vol.Schema({
            vol.Required(CONF_SERIAL_PORT): vol.In(ports),
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        })

        return self.async_show_form(
            step_id="serial",
            data_schema=schema,
            errors=errors
        )

    async def async_step_amp_config(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle amplifier configuration."""
        if user_input is not None:
            # Combine all configuration
            self.config.update(user_input)

            # Create unique ID to prevent duplicate configs
            if self.config[CONF_CONNECTION_TYPE] == CONNECTION_TCP:
                unique_id = f"{self.config[CONF_TCP_HOST]}:{self.config[CONF_TCP_PORT]}"
            else:
                unique_id = self.config[CONF_SERIAL_PORT]

            # Check if already configured
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            # Create the config entry
            return self.async_create_entry(
                title=self.config[CONF_NAME],
                data=self.config
            )

        schema = vol.Schema({
            vol.Required(CONF_AMP_TYPE): vol.In(AMP_TYPES),
            vol.Optional(CONF_CXN_IP): str,
        })

        return self.async_show_form(
            step_id="amp_config",
            data_schema=schema,
            description_placeholders={
                "info": "CXN IP is optional - only needed for volume control via CXN"
            }
        )

    async def _test_tcp_connection(self, host: str, port: int) -> bool:
        """Test TCP connection to device."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)

            # Run connection in executor to avoid blocking
            result = await self.hass.async_add_executor_job(
                sock.connect_ex, (host, port)
            )
            sock.close()

            # connect_ex returns 0 on success
            return result == 0
        except Exception:
            return False

    async def _test_serial_connection(self, port: str) -> bool:
        """Test serial connection to device."""
        try:
            # Try to open port with CXA settings
            ser = await self.hass.async_add_executor_job(
                serial.Serial, port, 9600, timeout=1
            )
            ser.close()
            return True
        except Exception:
            return False

    def _get_serial_ports(self) -> Dict[str, str]:
        """Get available serial ports."""
        ports = {}
        for port in serial.tools.list_ports.comports():
            # Create friendly description
            ports[port.device] = f"{port.device} - {port.description}"
        return ports

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return CambridgeCXAOptionsFlow(config_entry)


class CambridgeCXAOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Cambridge CXA."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Save the new options
            return self.async_create_entry(title="", data=user_input)

        # Show form with current values as defaults
        schema = vol.Schema({
            vol.Optional(
                CONF_CXN_IP,
                default=self.config_entry.data.get(CONF_CXN_IP, "")
            ): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)