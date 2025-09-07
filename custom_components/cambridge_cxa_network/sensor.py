"""Sensor platform for Cambridge CXA Network integration."""
import logging
from typing import Optional, Any

from datetime import timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Scan interval for sensors (1 minute)
SCAN_INTERVAL = timedelta(minutes=1)

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="power_state",
        name="Power State",
        icon="mdi:power",
    ),
    SensorEntityDescription(
        key="current_source",
        name="Current Source",
        icon="mdi:audio-input-stereo-minijack",
    ),
    SensorEntityDescription(
        key="mute_state",
        name="Mute State",
        icon="mdi:volume-mute",
    ),
    SensorEntityDescription(
        key="speaker_output",
        name="Speaker Output",
        icon="mdi:speaker-multiple",
    ),
    SensorEntityDescription(
        key="volume",
        name="Volume",
        icon="mdi:volume-high",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="max_volume",
        name="Max Volume",
        icon="mdi:volume-source",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="connection_status",
        name="Connection Status",
        icon="mdi:connection",
    ),
    SensorEntityDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:chip",
    ),
    SensorEntityDescription(
        key="protocol_version",
        name="Protocol Version",
        icon="mdi:file-document",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge CXA sensors."""
    # Get the media player entity
    entities = []
    
    for description in SENSOR_DESCRIPTIONS:
        entities.append(
            CambridgeCXASensor(
                hass,
                entry,
                description,
            )
        )
    
    async_add_entities(entities, True)


class CambridgeCXASensor(SensorEntity):
    """Representation of a Cambridge CXA sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get("name", "Cambridge CXA"),
            manufacturer="Cambridge Audio",
            model=entry.data.get("amp_type", "CXA"),
        )
        self._attr_native_value = None

    async def async_update(self) -> None:
        """Update the sensor state."""
        # Get the media player entity
        media_player_entity_id = f"media_player.{self._entry.data.get('name', 'cambridge_cxa').lower().replace(' ', '_')}"
        media_player = self._hass.states.get(media_player_entity_id)
        
        if not media_player:
            self._attr_native_value = "Unavailable"
            return
        
        # Update based on sensor type
        if self.entity_description.key == "power_state":
            self._attr_native_value = media_player.state
        elif self.entity_description.key == "current_source":
            self._attr_native_value = media_player.attributes.get("source", "Unknown")
        elif self.entity_description.key == "mute_state":
            self._attr_native_value = "Muted" if media_player.attributes.get("is_volume_muted", False) else "Unmuted"
        elif self.entity_description.key == "speaker_output":
            self._attr_native_value = media_player.attributes.get("sound_mode", "Unknown")
        elif self.entity_description.key == "connection_status":
            self._attr_native_value = "Connected" if media_player.state != "unavailable" else "Disconnected"
        elif self.entity_description.key == "volume":
            self._attr_native_value = media_player.attributes.get("volume", 0)
        elif self.entity_description.key == "max_volume":
            self._attr_native_value = media_player.attributes.get("max_volume", 96)
        elif self.entity_description.key == "firmware_version":
            self._attr_native_value = media_player.attributes.get("firmware_version", "Unknown")
        elif self.entity_description.key == "protocol_version":
            self._attr_native_value = media_player.attributes.get("protocol_version", "Unknown")