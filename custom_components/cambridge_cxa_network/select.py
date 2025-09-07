"""Select platform for Cambridge CXA Network integration."""
import logging
from typing import Any

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SOUND_MODES,
)

_LOGGER = logging.getLogger(__name__)

SELECT_DESCRIPTIONS = [
    SelectEntityDescription(
        key="speaker_output",
        name="Speaker Output",
        icon="mdi:speaker-multiple",
        options=["A", "AB", "B"],
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge CXA select entities."""
    entities = []
    
    for description in SELECT_DESCRIPTIONS:
        entities.append(
            CambridgeCXASelect(
                hass,
                entry,
                description,
            )
        )
    
    async_add_entities(entities, True)


class CambridgeCXASelect(SelectEntity):
    """Representation of a Cambridge CXA select entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
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
        self._attr_current_option = None

    async def async_update(self) -> None:
        """Update the select state."""
        # Get the media player entity
        media_player_entity_id = f"media_player.{self._entry.data.get('name', 'cambridge_cxa').lower().replace(' ', '_')}"
        media_player = self._hass.states.get(media_player_entity_id)
        
        if not media_player:
            return
        
        # Update based on select type
        if self.entity_description.key == "speaker_output":
            sound_mode = media_player.attributes.get("sound_mode", None)
            if sound_mode in self.options:
                self._attr_current_option = sound_mode

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Get the media player entity
        media_player_entity_id = f"media_player.{self._entry.data.get('name', 'cambridge_cxa').lower().replace(' ', '_')}"
        
        # Call the sound mode service on the media player
        await self._hass.services.async_call(
            "media_player",
            "select_sound_mode",
            {
                "entity_id": media_player_entity_id,
                "sound_mode": option,
            },
            blocking=True,
        )
        
        self._attr_current_option = option