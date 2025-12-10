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
        # Get the media player entity from the same integration
        media_player = None
        
        # Find the media player entity from our device
        device_registry = self._hass.helpers.device_registry.async_get()
        entity_registry = self._hass.helpers.entity_registry.async_get()
        
        # Get our device
        device = device_registry.async_get_device(identifiers={(DOMAIN, self._entry.entry_id)})
        
        if device:
            # Find media player entity for this device
            for entity in entity_registry.entities.values():
                if entity.device_id == device.id and entity.domain == "media_player":
                    media_player = self._hass.states.get(entity.entity_id)
                    break
        
        if not media_player:
            # Fallback - try common entity IDs
            for entity_id in ["media_player.cambridge_audio_cxa", 
                              f"media_player.{self._entry.data.get('name', 'cambridge_cxa').lower().replace(' ', '_')}"]:
                media_player = self._hass.states.get(entity_id)
                if media_player:
                    break
        
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
        elif self.entity_description.key == "firmware_version":
            self._attr_native_value = media_player.attributes.get("firmware_version", "Unknown")
        elif self.entity_description.key == "protocol_version":
            # We store model name now, not protocol version
            self._attr_native_value = media_player.attributes.get("model", "Unknown")