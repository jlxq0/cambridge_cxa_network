"""Number platform for Cambridge CXA Network integration."""
import logging
from typing import Any

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

NUMBER_DESCRIPTIONS = [
    NumberEntityDescription(
        key="volume",
        name="Volume",
        icon="mdi:volume-high",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.SLIDER,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge CXA number entities."""
    # Volume control only available if CXN is configured
    # RS232 protocol does not support volume control
    
    from .const import CONF_CXN_IP
    
    # Only add volume control if CXN is configured
    if not entry.data.get(CONF_CXN_IP):
        _LOGGER.info("No CXN IP configured, volume control not available via RS232")
        return
    
    entities = []
    
    for description in NUMBER_DESCRIPTIONS:
        entities.append(
            CambridgeCXANumber(
                hass,
                entry,
                description,
            )
        )
    
    async_add_entities(entities, True)


class CambridgeCXANumber(NumberEntity):
    """Representation of a Cambridge CXA number control."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
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
        self._attr_native_value = 0

    async def async_update(self) -> None:
        """Update the number state."""
        # Get the media player entity
        media_player_entity_id = f"media_player.{self._entry.data.get('name', 'cambridge_cxa').lower().replace(' ', '_')}"
        media_player = self._hass.states.get(media_player_entity_id)
        
        if not media_player:
            return
        
        # For now, we can't read the volume from the amplifier
        # This would require CXN integration
        if self.entity_description.key == "volume":
            # TODO: Implement volume reading when CXN protocol is known
            pass

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Get the media player entity
        media_player_entity_id = f"media_player.{self._entry.data.get('name', 'cambridge_cxa').lower().replace(' ', '_')}"
        
        # Find the media player entity and call volume control
        media_player = self._hass.data.get("media_player")
        if not media_player:
            _LOGGER.error("Could not find media_player platform")
            return
            
        for entity in media_player.entities:
            if entity.entity_id == media_player_entity_id:
                # Since we don't have direct volume control via CXA protocol,
                # we'll use the CXN HTTP API through the media player
                # The media player should implement volume control via CXN
                current_volume = self._attr_native_value or 0
                steps = int(value - current_volume)
                
                if steps > 0:
                    for _ in range(steps):
                        await entity.async_volume_up()
                elif steps < 0:
                    for _ in range(abs(steps)):
                        await entity.async_volume_down()
                
                self._attr_native_value = value
                break