"""Component that couples few alarm to keep their states in sync."""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.event import track_state_change

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY, STATE_ALARM_ARMED_HOME, STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED, STATE_ALARM_TRIGGERED,
    ATTR_ENTITY_ID)

_LOGGER = logging.getLogger(__name__)

ALARM_DOMAIN = "alarm_control_panel"

DOMAIN = "coupled_alarms"
ENTITY_ID_FORMAT = DOMAIN + ".{}"

CONF_ENTITIES = "entities"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: cv.schema_with_slug_keys(
        vol.Any({
            vol.Optional(CONF_ENTITIES, default={}): cv.entity_ids
        }, None)
    )
}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    """Set up a timer."""
    _LOGGER.debug("Couples setting up...")

    component = EntityComponent(_LOGGER, DOMAIN, hass)

    entities = []
    object_ids = []

    for couple_name, cfg in config[DOMAIN].items():
        if not cfg:
            cfg = {}
        ids = cfg[CONF_ENTITIES]
        object_ids = object_ids + ids
        entities.append(CoupledAlarms(hass, couple_name, ids))

    if not entities:
        return False

    component.add_entities(entities)

    def notify_state_change(entity_id, old_state, new_state):
        for entity in entities:
            entity.state_changed(entity_id, old_state, new_state)

    track_state_change(hass, object_ids, notify_state_change)

    return True

class CoupledAlarms(Entity):

    def __init__(self, hass, couple_name, object_ids):
        self._hass = hass
        self._couple_name = couple_name
        self._object_ids = object_ids

        self.entity_id = ENTITY_ID_FORMAT.format(couple_name)
        self._state = None

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._couple_name

    @property
    def state(self):
        return self._state

    def state_changed(self, entity_id, old_state, new_state):
        if entity_id in self._object_ids:
            for object_id in self._object_ids:
                if object_id != entity_id:
                    if object_id in self._hass.states._states:
                        object_id_old_state = self._hass.states.get(object_id)
                        if object_id_old_state.state != new_state.state:
                            _LOGGER.debug("Setting coulped state")
                            _LOGGER.debug("State: " + str(new_state.state))
                            _LOGGER.debug("From: " + str(entity_id))
                            _LOGGER.debug("To: " + str(object_id))
                            data = {ATTR_ENTITY_ID: object_id}
                            #data[ATTR_ENTITY_ID] = object_id
                            if new_state.state == STATE_ALARM_ARMED_AWAY:
                                self._hass.services.call(ALARM_DOMAIN, "alarm_arm_away", data)
                            elif new_state.state == STATE_ALARM_ARMED_HOME:
                                self._hass.services.call(ALARM_DOMAIN, "alarm_arm_home", data)
                            elif new_state.state == STATE_ALARM_ARMED_NIGHT:
                                self._hass.services.call(ALARM_DOMAIN, "alarm_arm_night", data)
                            elif new_state.state == STATE_ALARM_DISARMED:
                                self._hass.services.call(ALARM_DOMAIN, "alarm_disarm", data)
                            elif new_state.state == STATE_ALARM_TRIGGERED:
                                self._hass.services.call(ALARM_DOMAIN, "alarm_trigger", data)
