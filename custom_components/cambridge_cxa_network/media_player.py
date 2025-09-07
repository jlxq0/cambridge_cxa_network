"""
Support for controlling a Cambridge Audio CXA amplifier over a serial or network connection.

Original implementation by @lievencoghe
Network support added by @jlxq0

For more details about this platform, please refer to the documentation at
https://github.com/jlxq0/cambridge_cxa_network
"""

import logging
import urllib.request
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
from homeassistant.const import CONF_NAME, STATE_OFF, STATE_ON

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
    AMP_CMD_GET_PWSTATE,
    AMP_CMD_GET_CURRENT_SOURCE,
    AMP_CMD_GET_MUTE_STATE,
    AMP_CMD_SET_MUTE_ON,
    AMP_CMD_SET_MUTE_OFF,
    AMP_CMD_SET_PWR_ON,
    AMP_CMD_SET_PWR_STANDBY,
    AMP_CMD_GET_FIRMWARE_VERSION,
    AMP_CMD_GET_PROTOCOL_VERSION,
    AMP_CMD_SELECT_NEXT_SOURCE,
    AMP_CMD_SELECT_PREV_SOURCE,
    AMP_CMD_GET_VOLUME,
    AMP_CMD_SET_VOLUME,
    AMP_CMD_INCREASE_VOLUME,
    AMP_CMD_DECREASE_VOLUME,
    AMP_REPLY_PWR_ON,
    AMP_REPLY_PWR_STANDBY,
    AMP_REPLY_MUTE_ON,
    AMP_REPLY_MUTE_OFF,
    AMP_REPLY_FIRMWARE_VERSION,
    AMP_REPLY_PROTOCOL_VERSION,
    AMP_REPLY_VOLUME,
    NORMAL_INPUTS_CXA61,
    NORMAL_INPUTS_CXA81,
    NORMAL_INPUTS_AMP_REPLY_CXA61,
    NORMAL_INPUTS_AMP_REPLY_CXA81,
    SOUND_MODES,
    DEFAULT_TIMEOUT,
)

__version__ = "2.0.0"

_LOGGER = logging.getLogger(__name__)

# Update interval for sensors (1 minute)
SCAN_INTERVAL = 60

SUPPORT_CXA = (
    MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
)

SUPPORT_CXA_WITH_CXN = (
    MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
)

DEVICE_CLASS = "receiver"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge CXA from a config entry."""
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
        CambridgeCXADevice(
            hass,
            config[CONF_NAME],
            connection,
            config[CONF_AMP_TYPE],
            config.get(CONF_CXN_IP),
            entry.entry_id
        )
    ], True)


class TCPSerialConnection:
    """TCP connection wrapper that mimics serial interface."""

    def __init__(self, host: str, port: int):
        """Initialize TCP connection parameters."""
        self.host = host
        self.port = port
        self.timeout = DEFAULT_TIMEOUT
        self.socket = None
        self._lock = asyncio.Lock()

    async def connect(self):
        """Establish TCP connection to USR-W610."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.connect, (self.host, self.port)
            )
            _LOGGER.info(f"Connected to CXA via TCP at {self.host}:{self.port}")
        except Exception as e:
            _LOGGER.error(f"Failed to connect to {self.host}:{self.port}: {e}")
            self.socket = None

    async def ensure_connected(self):
        """Ensure we have an active connection."""
        if not self.socket:
            await self.connect()

    async def write(self, data: str):
        """Write data to TCP socket."""
        async with self._lock:
            await self.ensure_connected()
            if not self.socket:
                return

            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.socket.send, data.encode('utf-8')
                )
                _LOGGER.debug(f"Sent: {data.strip()}")
            except Exception as e:
                _LOGGER.error(f"Write failed: {e}")
                self.socket = None

    async def read_line(self) -> str:
        """Read a line from TCP socket."""
        if not self.socket:
            return ""

        try:
            # Set socket to non-blocking mode for async operation
            self.socket.setblocking(False)
            line = b''
            
            while True:
                try:
                    char = await asyncio.get_event_loop().sock_recv(self.socket, 1)
                    if not char:
                        break
                    if char == b'\r' or char == b'\n':
                        if line:  # Only break if we have data
                            break
                    else:
                        line += char
                except socket.error:
                    await asyncio.sleep(0.01)
                    continue
                    
            result = line.decode('utf-8', errors='ignore')
            if result:
                _LOGGER.debug(f"Received: {result}")
            return result
        except Exception as e:
            _LOGGER.error(f"Read failed: {e}")
            self.socket = None
            return ""

    def flush(self):
        """Flush the connection buffer."""
        if self.socket:
            self.socket.setblocking(False)
            try:
                while self.socket.recv(1024):
                    pass
            except:
                pass
            self.socket.setblocking(True)

    async def close(self):
        """Close TCP connection."""
        if self.socket:
            self.socket.close()
            self.socket = None
            _LOGGER.info("TCP connection closed")


class SerialConnection:
    """Serial connection wrapper for direct USB/RS232."""

    def __init__(self, device: str):
        """Initialize serial connection parameters."""
        self.device = device
        self.serial = None
        self._lock = asyncio.Lock()

    async def connect(self):
        """Open serial port with Cambridge parameters."""
        try:
            self.serial = await asyncio.get_event_loop().run_in_executor(
                None,
                serial.Serial,
                self.device,
                9600,
                serial.EIGHTBITS,
                serial.PARITY_NONE,
                serial.STOPBITS_ONE,
                DEFAULT_TIMEOUT
            )
            _LOGGER.info(f"Connected to CXA on {self.device}")
        except Exception as e:
            _LOGGER.error(f"Failed to open serial port {self.device}: {e}")
            self.serial = None

    async def ensure_connected(self):
        """Ensure serial port is open."""
        if not self.serial or not self.serial.is_open:
            await self.connect()

    async def write(self, data: str):
        """Write data to serial port."""
        async with self._lock:
            await self.ensure_connected()
            if not self.serial:
                return

            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.serial.write, data.encode('utf-8')
                )
                _LOGGER.debug(f"Serial sent: {data.strip()}")
            except Exception as e:
                _LOGGER.error(f"Serial write failed: {e}")
                self.serial = None

    async def read_line(self) -> str:
        """Read a line from serial port."""
        if not self.serial:
            return ""

        try:
            line = await asyncio.get_event_loop().run_in_executor(
                None, self.serial.readline
            )
            result = line.decode('utf-8', errors='ignore').strip()
            if result:
                _LOGGER.debug(f"Serial received: {result}")
            return result
        except Exception as e:
            _LOGGER.error(f"Serial read failed: {e}")
            return ""

    def flush(self):
        """Flush serial input buffer."""
        if self.serial:
            self.serial.flush()

    async def close(self):
        """Close serial port."""
        if self.serial:
            self.serial.close()
            self.serial = None


class CambridgeCXADevice(MediaPlayerEntity):
    """Representation of a Cambridge CXA amplifier."""

    def __init__(
        self,
        hass,
        name: str,
        connection: Any,
        amp_type: str,
        cxn_ip: Optional[str],
        entry_id: str
    ):
        """Initialize the Cambridge CXA entity."""
        _LOGGER.debug("Setting up Cambridge CXA")
        self._hass = hass
        self._name = name
        self._connection = connection
        self._amp_type = amp_type.upper()
        self._cxn_ip = cxn_ip
        self._entry_id = entry_id
        
        # State variables
        self._mediasource = "#04,01,00"
        self._speakersactive = ""
        self._muted = AMP_REPLY_MUTE_OFF
        self._pwstate = ""
        self._state = STATE_OFF
        self._firmware_version = None
        self._protocol_version = None
        self._volume = None
        self._max_volume = 96  # CXA81 volume range is 0-96
        
        # Set up source lists based on amp type
        if self._amp_type == "CXA61":
            self._source_list = NORMAL_INPUTS_CXA61.copy()
            self._source_reply_list = NORMAL_INPUTS_AMP_REPLY_CXA61.copy()
        else:
            self._source_list = NORMAL_INPUTS_CXA81.copy()
            self._source_reply_list = NORMAL_INPUTS_AMP_REPLY_CXA81.copy()
        self._sound_mode_list = SOUND_MODES.copy()
        
    async def async_update(self):
        """Update device state."""
        try:
            self._pwstate = await self._command_with_reply(AMP_CMD_GET_PWSTATE)
        except Exception as e:
            _LOGGER.error(f"Failed to update device state: {e}")
            self._state = "unavailable"
            return
            
        if self._pwstate and AMP_REPLY_PWR_ON in self._pwstate:
            self._state = STATE_ON
        elif self._pwstate and AMP_REPLY_PWR_STANDBY in self._pwstate:
            self._state = STATE_OFF
        else:
            # If we can't determine power state, try to query other values anyway
            _LOGGER.warning("Could not determine power state, attempting to query other values")
            self._state = "unknown"
        
        # Try to get values regardless of power state
        if self._state != "unavailable":
            # Get source
            try:
                self._mediasource = await self._command_with_reply(AMP_CMD_GET_CURRENT_SOURCE)
            except Exception:
                _LOGGER.debug("Failed to get current source")
            
            # Get mute state
            try:
                self._muted = await self._command_with_reply(AMP_CMD_GET_MUTE_STATE)
            except Exception:
                _LOGGER.debug("Failed to get mute state")
            
            # Get volume information
            try:
                vol_reply = await self._command_with_reply(AMP_CMD_GET_VOLUME)
                if vol_reply and vol_reply.startswith(AMP_REPLY_VOLUME):
                    try:
                        self._volume = int(vol_reply.replace(AMP_REPLY_VOLUME, ""))
                    except ValueError:
                        pass
            except Exception:
                _LOGGER.debug("Failed to get volume")
            
            
            # Get firmware and protocol versions (only need to query occasionally)
            if self._firmware_version is None:
                try:
                    fw_reply = await self._command_with_reply(AMP_CMD_GET_FIRMWARE_VERSION)
                    if fw_reply and fw_reply.startswith(AMP_REPLY_FIRMWARE_VERSION):
                        self._firmware_version = fw_reply.replace(AMP_REPLY_FIRMWARE_VERSION, "")
                except Exception:
                    _LOGGER.debug("Failed to get firmware version")
            
            if self._protocol_version is None:
                try:
                    pv_reply = await self._command_with_reply(AMP_CMD_GET_PROTOCOL_VERSION)
                    if pv_reply and pv_reply.startswith(AMP_REPLY_PROTOCOL_VERSION):
                        self._protocol_version = pv_reply.replace(AMP_REPLY_PROTOCOL_VERSION, "")
                except Exception:
                    _LOGGER.debug("Failed to get protocol version")

    async def _command(self, command):
        """Send a command to the amplifier."""
        try:
            self._connection.flush()
            await self._connection.write(command + "\r")
            self._connection.flush()
        except:
            _LOGGER.error("Could not send command")
    
    async def _command_with_reply(self, command):
        """Send a command and wait for reply."""
        try:
            await self._connection.write(command + "\r")
            reply = await self._connection.read_line()
            return reply
        except:
            _LOGGER.error("Could not send command")
            return ""

    def url_command(self, command):
        """Send command to CXN via HTTP."""
        if self._cxn_ip:
            try:
                urllib.request.urlopen("http://" + self._cxn_ip + "/" + command).read()
            except:
                _LOGGER.error("Failed to send command to CXN")

    @property
    def unique_id(self):
        """Return unique ID for this entity."""
        return self._entry_id

    @property
    def is_volume_muted(self):
        """Return mute state."""
        return AMP_REPLY_MUTE_ON in self._muted
    
    @property
    def volume_level(self):
        """Return the volume level (0..1)."""
        if self._volume is not None and self._max_volume:
            return self._volume / self._max_volume
        return None

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def source(self):
        """Return current input source."""
        return self._source_reply_list.get(self._mediasource, "Unknown")

    @property
    def sound_mode(self):
        """Return current sound mode."""
        return self._speakersactive

    @property
    def sound_mode_list(self):
        """Return list of available sound modes."""
        return sorted(list(self._sound_mode_list.keys()))

    @property
    def source_list(self):
        """Return list of available sources."""
        return sorted(list(self._source_list.keys()))

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def supported_features(self):
        """Return features this device supports."""
        if self._cxn_ip:
            return SUPPORT_CXA_WITH_CXN
        return SUPPORT_CXA
    
    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attrs = {}
        if self._firmware_version:
            attrs["firmware_version"] = self._firmware_version
        if self._protocol_version:
            attrs["protocol_version"] = self._protocol_version
        if self._speakersactive:
            attrs["speaker_output"] = self._speakersactive
        if self._volume is not None:
            attrs["volume"] = self._volume
        if self._max_volume is not None:
            attrs["max_volume"] = self._max_volume
        return attrs

    async def async_mute_volume(self, mute):
        """Mute or unmute audio."""
        if mute:
            await self._command(AMP_CMD_SET_MUTE_ON)
        else:
            await self._command(AMP_CMD_SET_MUTE_OFF)

    async def async_select_sound_mode(self, sound_mode):
        """Select sound mode."""
        await self._command(self._sound_mode_list[sound_mode])

    async def async_select_source(self, source):
        """Select input source."""
        await self._command(self._source_list[source])

    async def async_turn_on(self):
        """Turn the amplifier on."""
        await self._command(AMP_CMD_SET_PWR_ON)

    async def async_turn_off(self):
        """Turn the amplifier off."""
        await self._command(AMP_CMD_SET_PWR_STANDBY)

    async def async_volume_up(self):
        """Increase volume by one step."""
        if self._cxn_ip:
            # Use CXN for volume control
            self.url_command("smoip/zone/state?pre_amp_mode=false")
            self.url_command("smoip/zone/volume?zone=1&command=step_up")
        else:
            # Use amplifier protocol
            await self._command(AMP_CMD_INCREASE_VOLUME)

    async def async_volume_down(self):
        """Decrease volume by one step."""
        if self._cxn_ip:
            # Use CXN for volume control
            self.url_command("smoip/zone/state?pre_amp_mode=false")
            self.url_command("smoip/zone/volume?zone=1&command=step_down")
        else:
            # Use amplifier protocol
            await self._command(AMP_CMD_DECREASE_VOLUME)
    
    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        if self._max_volume:
            # Convert 0..1 to 0..max_volume
            volume_int = int(volume * self._max_volume)
            # Format as two-digit string
            volume_str = f"{volume_int:02d}"
            await self._command(AMP_CMD_SET_VOLUME + volume_str)
    
    async def async_select_next_source(self):
        """Select next input source."""
        await self._command(AMP_CMD_SELECT_NEXT_SOURCE)
    
    async def async_select_prev_source(self):
        """Select previous input source."""
        await self._command(AMP_CMD_SELECT_PREV_SOURCE)

    async def async_will_remove_from_hass(self):
        """Clean up when entity is removed."""
        await self._connection.close()