"""Button platform for Cambridge CXA Network integration."""
import logging
from typing import Any

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    AMP_CMD_SELECT_NEXT_SOURCE,
    AMP_CMD_SELECT_PREV_SOURCE,
)

_LOGGER = logging.getLogger(__name__)

BUTTON_DESCRIPTIONS = [
    ButtonEntityDescription(
        key="next_source",
        name="Next Source",
        icon="mdi:skip-next",
    ),
    ButtonEntityDescription(
        key="previous_source", 
        name="Previous Source",
        icon="mdi:skip-previous",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cambridge CXA buttons."""
    entities = []
    
    for description in BUTTON_DESCRIPTIONS:
        entities.append(
            CambridgeCXAButton(
                hass,
                entry,
                description,
            )
        )
    
    async_add_entities(entities, True)


class CambridgeCXAButton(ButtonEntity):
    """Representation of a Cambridge CXA button."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
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

    async def async_press(self) -> None:
        """Handle the button press."""
        # Get the media player entity
        media_player_entity_id = f"media_player.{self._entry.data.get('name', 'cambridge_cxa').lower().replace(' ', '_')}"
        media_player = self._hass.data.get("media_player")
        
        if not media_player:
            _LOGGER.error(f"Could not find media_player platform")
            return
            
        # Get all media player entities and find ours
        for entity in media_player.entities:
            if entity.entity_id == media_player_entity_id:
                # Call the appropriate method on the media player entity
                if self.entity_description.key == "next_source":
                    await entity.async_select_next_source()
                    _LOGGER.info("Sent next source command")
                elif self.entity_description.key == "previous_source":
                    await entity.async_select_prev_source()
                    _LOGGER.info("Sent previous source command")
                break
        else:
            _LOGGER.error(f"Could not find media player entity: {media_player_entity_id}")