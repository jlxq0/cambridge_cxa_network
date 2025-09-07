# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Developing with this Home Assistant Custom Component

Since this is a Home Assistant custom component, testing requires a Home Assistant development environment:

- **Testing the component**: Set up a Home Assistant development environment and add the `cambridge_cxa` folder to your `custom_components` directory
- **Validating manifest.json**: Use Home Assistant's built-in validation when loading the component
- **Checking serial communication**: Test with a real Cambridge Audio CXA 61/81 amplifier or use a serial port emulator

## Architecture

This is a Home Assistant custom component for controlling Cambridge Audio CXA 61/81 amplifiers via serial connection.

### Key Components

1. **media_player.py** - Main implementation containing:
   - `CambridgeCXADevice` class that extends `MediaPlayerEntity`
   - Serial communication protocol using specific command strings (e.g., `#01,01` for power state)
   - Support for both direct serial connections and network serial (via ser2net/socat)
   - Optional CXN integration for volume control via HTTP commands

2. **Serial Protocol**:
   - Commands are sent as strings terminated with `\r`
   - Responses are read line by line
   - Command format: `#XX,XX[,XX]` (e.g., `#03,04,00` to select input A1)
   - Different input mappings for CXA61 vs CXA81 models

3. **Integration Features**:
   - Power on/off control
   - Input source selection (A1-A4, D1-D3, Bluetooth, USB, etc.)
   - Mute control
   - Sound mode selection (A, AB, B speaker outputs)
   - Volume control when paired with a Cambridge CXN streamer

### Configuration

The component expects configuration in Home Assistant's `configuration.yaml`:
- `device`: Serial device path (e.g., `/dev/serial/by-id/...` or `/dev/ttyCXA`)
- `type`: Model type (CXA61 or CXA81)
- `name`: Display name (optional)
- `slave`: CXN IP address for volume control (optional)

### HACS Support

The component includes HACS (Home Assistant Community Store) support via:
- `hacs.json` for HACS metadata
- `manifest.json` for Home Assistant integration metadata

## Instructions

# Cambridge CXA Network Integration - Complete Implementation Guide

## Project Overview

**Repository**: https://github.com/jlxq0/cambridge_cxa_network

**Goal**: Transform the Cambridge CXA Home Assistant integration from a serial-only solution to a network-capable integration that works with the USR-W610 WiFi-to-serial converter.

**Why This Matters**:
- The original integration requires physical USB/serial connection to Home Assistant
- This limits placement options (HA must be near the amplifier)
- Many users run HA in VMs or containers where USB passthrough is complicated
- The USR-W610 allows placing the amplifier anywhere with WiFi coverage
- Network connections are more reliable than USB in virtualized environments

## Architecture Decisions Explained

### Why Config Flow Instead of YAML?

**Problem**: YAML configuration requires users to:
- Edit files manually (error-prone)
- Know exact device paths or IPs
- Restart HA to test changes
- Cannot validate connections before saving

**Solution**: Config Flow provides:
- Step-by-step GUI wizard
- Connection validation before saving
- No manual file editing
- Runtime reconfiguration via Options Flow
- Automatic discovery potential (future enhancement)

### Why Maintain Dual Connection Support?

**Problem**: Forcing network-only would break existing setups

**Solution**: Abstract connection layer that:
- Supports both TCP and serial transparently
- Uses same command protocol for both
- Allows users to migrate at their pace
- Maintains backward compatibility

### Why Async Implementation?

**Problem**: Synchronous I/O blocks Home Assistant's event loop

**Solution**: Async/await pattern:
- Non-blocking network operations
- Better performance with multiple devices
- Proper timeout handling
- Graceful error recovery

## Technical Implementation Details

### Connection Abstraction Layer

**Why**: The amplifier doesn't care if commands come via serial or network - it's just bytes in/out. We create a common interface so the main code doesn't need to know which transport is used.

**How**: Two connection classes with identical methods:
- `TCPSerialConnection`: Handles network communication
- `SerialConnection`: Handles USB/serial communication
- Both implement: `write()`, `read()`, `readline()`, `connect()`, `close()`

**What**: This allows the main `CambridgeCXA` class to work with either connection type without modification.

## File-by-File Implementation

### File 1: manifest.json

**Purpose**: Tells Home Assistant about our integration

```json
{
  "domain": "cambridge_cxa",
  "name": "Cambridge Audio CXA Network",
  "documentation": "https://github.com/jlxq0/cambridge_cxa_network",
  "issue_tracker": "https://github.com/jlxq0/cambridge_cxa_network/issues",
  "dependencies": [],
  "codeowners": ["@lievencoghe", "@jlxq0"],
  "requirements": ["pyserial==3.5"],
  "config_flow": true,
  "version": "2.0.0",
  "iot_class": "local_polling"
}
```

**Key Points**:
- `config_flow: true` - Enables GUI configuration
- `requirements`: pyserial for serial port support
- `iot_class: local_polling` - We poll device status regularly
- `codeowners` - Credits original author and you

### File 2: const.py

**Purpose**: Central location for all constants to avoid magic numbers/strings

```python
"""Constants for Cambridge CXA integration.

Original implementation by @lievencoghe
Network support added by @jlxq0

This file contains all protocol commands and configuration constants.
"""

DOMAIN = "cambridge_cxa"
DEFAULT_NAME = "Cambridge CXA"

# Network defaults - USR-W610 typically uses port 8899
DEFAULT_PORT = 8899
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
DEFAULT_TIMEOUT = 1.0

# Configuration keys
CONF_CONNECTION_TYPE = "connection_type"
CONF_TCP_HOST = "tcp_host"
CONF_TCP_PORT = "tcp_port"
CONF_SERIAL_PORT = "serial_port"
CONF_AMP_TYPE = "amp_type"
CONF_CXN_IP = "cxn_ip"  # Optional Cambridge CXN for volume sync

CONNECTION_TCP = "tcp"
CONNECTION_SERIAL = "serial"

AMP_TYPES = ["CXA61", "CXA81"]

# Cambridge Audio Protocol Commands
# These are documented in the CXA service manual
# Format: #<group>,<command>[,<parameter>]\r

# Power commands (Group 01)
CMD_POWER_ON = "#01,11\r"   # Turn amplifier on
CMD_POWER_OFF = "#01,12\r"  # Turn amplifier off
CMD_GET_STATUS = "#01,01,\r" # Get power status

# Volume commands (Group 01 for step, Group 03 for absolute)
CMD_VOLUME_UP = "#01,01\r"   # Increase volume by 1 step
CMD_VOLUME_DOWN = "#01,02\r" # Decrease volume by 1 step
CMD_MUTE_ON = "#01,03\r"     # Mute audio
CMD_MUTE_OFF = "#01,04\r"    # Unmute audio

# Query commands (Group 03)
CMD_GET_VERSION = "#01,02,\r"  # Get firmware version
CMD_GET_VOLUME = "#03,01,\r"   # Get current volume (0-96)
CMD_SET_VOLUME = "#03,02,"     # Set volume (add value + \r)
CMD_GET_SOURCE = "#03,03,\r"   # Get active input
CMD_SET_SOURCE = "#03,04,"     # Set input (add source + \r)
CMD_GET_MUTE = "#03,05,\r"     # Get mute status

# Input source codes
# These map to physical inputs on the amplifier
SOURCE_A1 = "01"   # Analogue input 1 (RCA)
SOURCE_A2 = "02"   # Analogue input 2 (RCA)
SOURCE_A3 = "03"   # Analogue input 3 (RCA)
SOURCE_A4 = "04"   # Analogue input 4 (RCA)
SOURCE_D1 = "05"   # Digital input 1 (Coaxial)
SOURCE_D2 = "06"   # Digital input 2 (Optical)
SOURCE_D3 = "07"   # Digital input 3 (Optical)
SOURCE_BT = "14"   # Bluetooth
SOURCE_USB = "16"  # USB input (CXA81 only)
SOURCE_XLR = "00"  # Balanced XLR (CXA81 only)

# Human-readable source names
SOURCE_MAP = {
    "A1": SOURCE_A1,
    "A2": SOURCE_A2,
    "A3": SOURCE_A3,
    "A4": SOURCE_A4,
    "D1": SOURCE_D1,
    "D2": SOURCE_D2,
    "D3": SOURCE_D3,
    "Bluetooth": SOURCE_BT,
    "USB": SOURCE_USB,
    "XLR": SOURCE_XLR,
}

# Reverse mapping for status queries
SOURCE_MAP_REVERSE = {v: k for k, v in SOURCE_MAP.items()}
```

**Why These Commands**: The Cambridge protocol uses a simple text format:
- `#` starts a command
- Two digits for command group
- Command number
- Optional parameters
- `\r` (carriage return) ends the command

### File 3: __init__.py

**Purpose**: Integration setup and lifecycle management

```python
"""The Cambridge CXA integration.

This file handles the integration lifecycle:
1. Loading configuration from the UI
2. Setting up the media player platform
3. Handling configuration updates
4. Cleanup on removal

Original implementation by @lievencoghe
Network support added by @jlxq0
"""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# We only have media_player platform
PLATFORMS = [Platform.MEDIA_PLAYER]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cambridge CXA from a config entry.

    This is called when the integration is loaded. It:
    1. Stores the config in hass.data for the platform to access
    2. Forwards setup to the media_player platform
    3. Registers an update listener for config changes
    """
    # Store config where media_player.py can access it
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Tell HA to set up our media_player platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for config updates (when user changes options)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Called when integration is removed or reloaded.
    Cleanly shuts down the media player and removes config.
    """
    # Unload the media_player platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove config from memory
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry.

    Called when user updates configuration options.
    We unload and reload to apply changes.
    """
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
```

### File 4: config_flow.py

**Purpose**: GUI configuration wizard

```python
"""Config flow for Cambridge CXA integration.

This creates the configuration UI that users see when adding the integration.
It's a multi-step wizard that:
1. Asks for connection type (Network or Serial)
2. Configures the selected connection
3. Tests the connection
4. Asks for amplifier model
5. Saves the configuration

Original implementation by @lievencoghe
Network support added by @jlxq0
"""
import socket
import serial
import serial.tools.list_ports
import voluptuous as vol
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
    """Handle a config flow for Cambridge CXA.

    This class defines each step of the configuration wizard.
    Home Assistant calls our methods in sequence as the user
    progresses through the wizard.
    """

    VERSION = 1  # Version of our config schema

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step.

        This is the entry point when user clicks "Add Integration".
        We ask them to choose between Network and Serial connection.
        """
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
        """Handle TCP configuration.

        Ask for IP address and port of the USR-W610.
        Test the connection before proceeding.
        """
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
        """Handle serial configuration.

        Show list of available serial ports.
        Test the selected port before proceeding.
        """
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
        """Handle amplifier configuration.

        Final step - ask for amplifier model and optional CXN IP.
        The CXN IP is used if you have a Cambridge streamer and
        want to control volume through it.
        """
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
        """Test TCP connection to device.

        Try to open a socket to the specified host:port.
        This validates the USR-W610 is reachable.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout

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
        """Test serial connection to device.

        Try to open the serial port with correct settings.
        This validates the USB/serial adapter is working.
        """
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
        """Get available serial ports.

        Uses pyserial to enumerate all serial ports on the system.
        Returns dict of {device: description} for the dropdown.
        """
        ports = {}
        for port in serial.tools.list_ports.comports():
            # Create friendly description
            ports[port.device] = f"{port.device} - {port.description}"
        return ports

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get options flow.

        This allows users to modify configuration after initial setup.
        """
        return CambridgeCXAOptionsFlow(config_entry)


class CambridgeCXAOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Cambridge CXA.

    This appears when user clicks "Configure" on an existing integration.
    Currently only allows changing the CXN IP address.
    """

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
```

### File 5: media_player.py

**Purpose**: The actual device control logic

```python
"""Support for Cambridge Audio CXA amplifiers.

This is the main logic that:
1. Creates the connection (TCP or Serial)
2. Sends commands to the amplifier
3. Reads responses and updates state
4. Provides media player interface to Home Assistant

The Cambridge protocol is simple text commands over serial/TCP.
Commands are acknowledged with responses we parse for state.

Original implementation by @lievencoghe
Network support added by @jlxq0
"""
import logging
import socket
import serial
import asyncio
from typing import Optional, Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_CONNECTION_TYPE,
    CONF_TCP_HOST,
    CONF_TCP_PORT,
    CONF_SERIAL_PORT,
    CONF_AMP_TYPE,
    CONF_CXN_IP,
    CONNECTION_TCP,
    CONNECTION_SERIAL,
    CMD_POWER_ON,
    CMD_POWER_OFF,
    CMD_VOLUME_UP,
    CMD_VOLUME_DOWN,
    CMD_MUTE_ON,
    CMD_MUTE_OFF,
    CMD_GET_STATUS,
    CMD_GET_VOLUME,
    CMD_SET_VOLUME,
    CMD_GET_SOURCE,
    CMD_SET_SOURCE,
    CMD_GET_MUTE,
    SOURCE_MAP,
    SOURCE_MAP_REVERSE,
)

_LOGGER = logging.getLogger(__name__)

# Define what features our media player supports
SUPPORT_CXA = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.SELECT_SOURCE
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge CXA from a config entry.

    Called by Home Assistant when setting up our platform.
    Creates the appropriate connection type and media player entity.
    """
    # Get config from storage
    config = hass.data[DOMAIN][entry.entry_id]

    # Create appropriate connection based on config
    if config[CONF_CONNECTION_TYPE] == CONNECTION_TCP:
        # Network connection via USR-W610
        connection = TCPSerialConnection(
            config[CONF_TCP_HOST],
            config[CONF_TCP_PORT]
        )
    else:
        # Direct serial connection
        connection = SerialConnection(config[CONF_SERIAL_PORT])

    # Create and add the media player entity
    async_add_entities([
        CambridgeCXA(
            config[CONF_NAME],
            connection,
            config[CONF_AMP_TYPE],
            config.get(CONF_CXN_IP),
            entry.entry_id
        )
    ], True)  # True = do initial update after adding


class TCPSerialConnection:
    """TCP connection wrapper that mimics serial interface.

    The USR-W610 creates a transparent bridge between TCP and serial.
    We send bytes over TCP, it sends them over serial to the amp.
    Responses come back the same way.

    This class makes TCP look like a serial port to the rest of the code.
    """

    def __init__(self, host: str, port: int, timeout: float = 1.0):
        """Initialize TCP connection parameters."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self._lock = asyncio.Lock()  # Prevent concurrent access

    async def connect(self):
        """Establish TCP connection to USR-W610.

        Creates a socket and connects to the device.
        Sets timeout to prevent hanging on reads.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)

            # Connect to USR-W610
            self.socket.connect((self.host, self.port))
            _LOGGER.info(f"Connected to CXA via TCP at {self.host}:{self.port}")
        except Exception as e:
            _LOGGER.error(f"Failed to connect to {self.host}:{self.port}: {e}")
            self.socket = None

    async def ensure_connected(self):
        """Ensure we have an active connection.

        Called before each operation to handle reconnection
        if the connection was lost.
        """
        if not self.socket:
            await self.connect()

    async def write(self, data: bytes):
        """Write data to TCP socket.

        Sends command bytes to the USR-W610, which forwards
        them to the amplifier over serial.
        """
        async with self._lock:  # Only one operation at a time
            await self.ensure_connected()

            if not self.socket:
                return  # Connection failed

            try:
                self.socket.send(data)
                _LOGGER.debug(f"Sent: {data}")
            except Exception as e:
                _LOGGER.error(f"Write failed: {e}")
                self.socket = None

                # Try to reconnect and retry once
                await self.connect()
                if self.socket:
                    try:
                        self.socket.send(data)
                    except Exception as e:
                        _LOGGER.error(f"Retry write failed: {e}")

    async def read(self, size: int = 1) -> bytes:
        """Read data from TCP socket.

        Reads response bytes from the amplifier via USR-W610.
        Returns empty bytes on timeout or error.
        """
        if not self.socket:
            return b''

        try:
            data = self.socket.recv(size)
            _LOGGER.debug(f"Received: {data}")
            return data
        except socket.timeout:
            # Normal - no data available
            return b''
        except Exception as e:
            _LOGGER.error(f"Read failed: {e}")
            self.socket = None
            return b''

    async def readline(self) -> bytes:
        """Read a line from TCP socket.

        Cambridge responses end with \n, so we read until we get one.
        """
        line = b''
        while True:
            char = await self.read(1)
            if not char or char == b'\n':
                break
            line += char

        if line:
            _LOGGER.debug(f"Read line: {line}")
        return line

    async def close(self):
        """Close TCP connection."""
        if self.socket:
            self.socket.close()
            self.socket = None
            _LOGGER.info("TCP connection closed")

    async def flush_input(self):
        """Flush input buffer.

        Clear any pending data to avoid reading old responses.
        """
        if self.socket:
            self.socket.setblocking(0)  # Non-blocking mode
            try:
                # Read and discard any pending data
                while self.socket.recv(1024):
                    pass
            except:
                pass  # No more data
            self.socket.setblocking(1)  # Back to blocking mode


class SerialConnection:
    """Serial connection wrapper for direct USB/RS232.

    This maintains compatibility with the original integration
    for users who have direct serial connections.
    """

    def __init__(self, device: str):
        """Initialize serial connection parameters."""
        self.device = device
        self.serial = None
        self._lock = asyncio.Lock()

    async def connect(self):
        """Open serial port with Cambridge parameters.

        9600 baud, 8 data bits, no parity, 1 stop bit (8N1)
        """
        try:
            self.serial = serial.Serial(
                self.device,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            _LOGGER.info(f"Connected to CXA on {self.device}")
        except Exception as e:
            _LOGGER.error(f"Failed to open serial port {self.device}: {e}")
            self.serial = None

    async def ensure_connected(self):
        """Ensure serial port is open."""
        if not self.serial or not self.serial.is_open:
            await self.connect()

    async def write(self, data: bytes):
        """Write data to serial port."""
        async with self._lock:
            await self.ensure_connected()

            if not self.serial:
                return

            try:
                self.serial.write(data)
                _LOGGER.debug(f"Serial sent: {data}")
            except Exception as e:
                _LOGGER.error(f"Serial write failed: {e}")
                self.serial = None

    async def read(self, size: int = 1) -> bytes:
        """Read data from serial port."""
        if not self.serial:
            return b''

        try:
            return self.serial.read(size)
        except Exception as e:
            _LOGGER.error(f"Serial read failed: {e}")
            return b''

    async def readline(self) -> bytes:
        """Read a line from serial port."""
        if not self.serial:
            return b''

        try:
            return self.serial.readline()
        except Exception as e:
            _LOGGER.error(f"Serial readline failed: {e}")
            return b''

    async def close(self):
        """Close serial port."""
        if self.serial:
            self.serial.close()
            self.serial = None

    async def flush_input(self):
        """Flush serial input buffer."""
        if self.serial:
            self.serial.flushInput()


class CambridgeCXA(MediaPlayerEntity):
    """Representation of a Cambridge CXA amplifier.

    This is the main entity that Home Assistant interacts with.
    It maintains state, sends commands, and updates from the device.
    """

    def __init__(
        self,
        name: str,
        connection: Any,
        amp_type: str,
        cxn_ip: Optional[str],
        entry_id: str
    ):
        """Initialize the Cambridge CXA entity."""
        self._name = name
        self._connection = connection  # TCP or Serial connection
        self._amp_type = amp_type      # CXA61 or CXA81
        self._cxn_ip = cxn_ip          # Optional CXN for volume
        self._entry_id = entry_id      # Unique ID for this config

        # State variables
        self._state = MediaPlayerState.OFF
        self._volume = 0        # 0-96 in CXA units
        self._muted = False
        self._source = None
        self._available = True  # Is device responding?

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self):
        """Return unique ID for this entity."""
        return self._entry_id

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def available(self):
        """Return True if device is responding."""
        return self._available

    @property
    def supported_features(self):
        """Return features this device supports."""
        return SUPPORT_CXA

    @property
    def volume_level(self):
        """Volume level 0..1 for Home Assistant."""
        # Convert CXA's 0-96 to HA's 0-1
        return self._volume / 96.0

    @property
    def is_volume_muted(self):
        """Return mute state."""
        return self._muted

    @property
    def source(self):
        """Return current input source."""
        return self._source

    @property
    def source_list(self):
        """Return list of available sources."""
        sources = list(SOURCE_MAP.keys())

        # Remove USB/XLR if CXA61 (they're CXA81 only)
        if self._amp_type == "CXA61":
            sources.remove("USB")
            sources.remove("XLR")

        return sources

    async def async_update(self):
        """Fetch new state data from amplifier.

        Called by Home Assistant to refresh device state.
        We query power, volume, source, and mute status.
        """
        try:
            # Query power status
            response = await self._send_command(CMD_GET_STATUS)
            if response:
                # Response format: #04,01,<status>\r
                # Status: 00=standby, 01=on
                if "#04,01,01" in response:
                    self._state = MediaPlayerState.ON
                else:
                    self._state = MediaPlayerState.OFF

            # Only query other states if powered on
            if self._state == MediaPlayerState.ON:
                # Get volume (0-96)
                response = await self._send_command(CMD_GET_VOLUME)
                if response and "#05,01," in response:
                    try:
                        # Parse volume from response
                        parts = response.split(",")
                        if len(parts) >= 3:
                            vol_str = parts[2].strip()
                            self._volume = int(vol_str)
                    except (ValueError, IndexError):
                        _LOGGER.warning(f"Failed to parse volume: {response}")

                # Get current source
                response = await self._send_command(CMD_GET_SOURCE)
                if response and "#05,03," in response:
                    try:
                        # Parse source code from response
                        parts = response.split(",")
                        if len(parts) >= 3:
                            src_code = parts[2].strip()
                            self._source = SOURCE_MAP_REVERSE.get(src_code, "Unknown")
                    except (ValueError, IndexError):
                        _LOGGER.warning(f"Failed to parse source: {response}")

                # Get mute status
                response = await self._send_command(CMD_GET_MUTE)
                if response and "#05,05," in response:
                    # Mute status: 00=unmuted, 01=muted
                    self._muted = ",01" in response

            # If we got here, device is responding
            self._available = True

        except Exception as e:
            _LOGGER.error(f"Error updating CXA: {e}")
            self._available = False

    async def async_turn_on(self):
        """Turn the amplifier on."""
        await self._send_command(CMD_POWER_ON)
        self._state = MediaPlayerState.ON

    async def async_turn_off(self):
        """Turn the amplifier off."""
        await self._send_command(CMD_POWER_OFF)
        self._state = MediaPlayerState.OFF

    async def async_volume_up(self):
        """Increase volume by one step."""
        await self._send_command(CMD_VOLUME_UP)
        # Device increments internally, we'll get new value on next update

    async def async_volume_down(self):
        """Decrease volume by one step."""
        await self._send_command(CMD_VOLUME_DOWN)

    async def async_set_volume_level(self, volume):
        """Set volume level 0..1."""
        # Convert HA's 0-1 to CXA's 0-96
        cxa_volume = int(volume * 96)

        # Ensure in valid range
        cxa_volume = max(0, min(96, cxa_volume))

        # Format command with volume value
        command = f"{CMD_SET_VOLUME}{cxa_volume:02d}\r"
        await self._send_command(command)
        self._volume = cxa_volume

    async def async_mute_volume(self, mute):
        """Mute or unmute audio."""
        if mute:
            await self._send_command(CMD_MUTE_ON)
        else:
            await self._send_command(CMD_MUTE_OFF)
        self._muted = mute

    async def async_select_source(self, source):
        """Select input source."""
        if source in SOURCE_MAP:
            # Get source code and send command
            source_code = SOURCE_MAP[source]
            command = f"{CMD_SET_SOURCE}{source_code}\r"
            await self._send_command(command)
            self._source = source

    async def _send_command(self, command: str) -> Optional[str]:
        """Send command to amplifier and return response.

        This is the core communication method. It:
        1. Sends a command
        2. Waits briefly for processing
        3. Reads the response
        4. Returns decoded response or None on error
        """
        try:
            # Send command as bytes
            await self._connection.write(command.encode())

            # Give device time to process and respond
            await asyncio.sleep(0.1)

            # Read response line
            response = await self._connection.readline()

            if response:
                # Decode and return response
                decoded = response.decode('utf-8', errors='ignore')
                _LOGGER.debug(f"Command: {command.strip()} -> Response: {decoded.strip()}")
                return decoded

        except Exception as e:
            _LOGGER.error(f"Error sending command {command}: {e}")
            self._available = False

        return None

    async def async_will_remove_from_hass(self):
        """Clean up when entity is removed.

        Called by Home Assistant when the integration is removed.
        We close the connection cleanly.
        """
        await self._connection.close()
```

### File 6: strings.json and translations/en.json

**Purpose**: User interface text for the configuration wizard

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Cambridge CXA Setup",
        "description": "Select how your Cambridge Audio amplifier is connected",
        "data": {
          "connection_type": "Connection Type"
        }
      },
      "tcp": {
        "title": "Network Configuration",
        "description": "Configure connection via USR-W610 or similar WiFi-to-serial device",
        "data": {
          "tcp_host": "IP Address",
          "tcp_port": "Port (usually 8899)",
          "name": "Device Name"
        }
      },
      "serial": {
        "title": "Serial Configuration",
        "description": "Configure direct USB or RS232 serial connection",
        "data": {
          "serial_port": "Serial Port",
          "name": "Device Name"
        }
      },
      "amp_config": {
        "title": "Amplifier Configuration",
        "description": "Select your amplifier model and optional settings",
        "data": {
          "amp_type": "Amplifier Model (CXA61 or CXA81)",
          "cxn_ip": "Cambridge CXN IP Address (optional - for volume sync)"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect - check IP address/port or serial connection",
      "unknown": "Unexpected error occurred"
    },
    "abort": {
      "already_configured": "This device is already configured"
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Cambridge CXA Options",
        "description": "Modify settings for your amplifier",
        "data": {
          "cxn_ip": "CXN IP Address (optional)"
        }
      }
    }
  }
}
```

## Implementation Steps

### Step 1: Create Repository Structure
```bash
# Create local repository
mkdir cambridge_cxa_network
cd cambridge_cxa_network
git init

# Create integration directory
mkdir -p custom_components/cambridge_cxa/translations

# Create all files as shown above
```

### Step 2: Test Locally
```bash
# Validate Python syntax
python3 -m py_compile custom_components/cambridge_cxa/*.py

# Validate JSON
python3 -c "import json; json.load(open('custom_components/cambridge_cxa/manifest.json'))"
```

### Step 3: Configure USR-W610

**Why These Settings**:
- **Mode: Server** - Device waits for connections from HA
- **Protocol: TCP** - Reliable delivery with error checking
- **Port: 8899** - Default for USR-W610, avoid conflicts
- **Serial: 9600 8N1** - Cambridge Audio standard settings

### Step 4: Deploy to Home Assistant

```bash
# Copy to Home Assistant
scp -r custom_components homeassistant@HA_IP:/config/

# Restart Home Assistant
ssh homeassistant@HA_IP "ha core restart"
```

### Step 5: Configure via GUI

1. **Settings → Devices & Services**
2. **Add Integration**
3. **Search "Cambridge"**
4. **Follow wizard**:
   - Choose Network
   - Enter USR-W610 IP
   - Test connection
   - Select amp model
   - Save

### Step 6: Verify Operation

```bash
# Monitor logs
ssh homeassistant@HA_IP "tail -f /config/home-assistant.log | grep -i cambridge"

# Test manually with netcat
echo -e "#01,01,\r" | nc USR_W610_IP 8899
```

## Troubleshooting Guide

### Connection Issues

**Problem**: "Failed to connect" error
**Solution**:
- Verify USR-W610 IP is correct
- Check port 8899 is not blocked
- Confirm USR-W610 is in Server mode
- Test with: `telnet USR_W610_IP 8899`

### No Response from Amplifier

**Problem**: Connected but no response
**Solution**:
- Check RS232 cable wiring (straight-through)
- Verify baud rate is 9600
- Ensure amplifier is powered on
- Try swapping TX/RX if using custom cable

### State Not Updating

**Problem**: Controls work but state doesn't update
**Solution**:
- Check response parsing in logs
- Verify firmware version compatibility
- Some commands may need longer delays

## Repository Structure

```
cambridge_cxa_network/
├── README.md
├── LICENSE
├── .gitignore
├── hacs.json                          # For HACS compatibility
└── custom_components/
    └── cambridge_cxa/
        ├── __init__.py                # Integration setup
        ├── manifest.json              # Integration metadata
        ├── config_flow.py             # GUI configuration
        ├── const.py                   # Constants
        ├── media_player.py            # Device control
        ├── strings.json               # UI strings
        └── translations/
            └── en.json                # English translations
```

## Git Commands

```bash
# Initial commit
git add .
git commit -m "Initial implementation of Cambridge CXA network integration

- Support for TCP/IP connection via USR-W610
- Maintains serial compatibility
- GUI configuration via config flow
- Based on original work by @lievencoghe"

# Add remote and push
git remote add origin https://github.com/jlxq0/cambridge_cxa_network.git
git branch -M main
git push -u origin main

# Create release
git tag v2.0.0 -m "Network support release"
git push origin v2.0.0
```

## Future Enhancements

1. **Auto-discovery**: mDNS/SSDP to find USR-W610 automatically
2. **Multiple amplifiers**: Support multiple CXA units
3. **Zone support**: If using CXA in multi-zone setup
4. **Status feedback**: Better parsing of all response codes
5. **HACS compatibility**: Add to HACS default reposit
