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
    NORMAL_INPUTS_CXA61,
    NORMAL_INPUTS_CXA81,
)

_LOGGER = logging.getLogger(__name__)

SELECT_DESCRIPTIONS = [
    SelectEntityDescription(
        key="speaker_output",
        name="Speaker Output",
        icon="mdi:speaker-multiple",
        options=["A", "AB", "B"],
    ),
    SelectEntityDescription(
        key="source",
        name="Source",
        icon="mdi:audio-input-stereo-minijack",
        options=[],  # Will be populated based on amp type
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
        
        # Set options based on entity type
        if description.key == "source":
            amp_type = entry.data.get("amp_type", "CXA61").upper()
            if amp_type == "CXA61":
                self._attr_options = list(NORMAL_INPUTS_CXA61.keys())
            else:
                self._attr_options = list(NORMAL_INPUTS_CXA81.keys())
        else:
            self._attr_options = description.options

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
        elif self.entity_description.key == "source":
            source = media_player.attributes.get("source", None)
            if source in self.options:
                self._attr_current_option = source

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Get the media player entity
        media_player_entity_id = f"media_player.{self._entry.data.get('name', 'cambridge_cxa').lower().replace(' ', '_')}"
        
        if self.entity_description.key == "speaker_output":
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
        elif self.entity_description.key == "source":
            # Call the source selection service on the media player
            await self._hass.services.async_call(
                "media_player",
                "select_source",
                {
                    "entity_id": media_player_entity_id,
                    "source": option,
                },
                blocking=True,
            )
        
        self._attr_current_option = option