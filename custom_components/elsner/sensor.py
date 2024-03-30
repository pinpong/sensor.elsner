from __future__ import annotations

import asyncio
import logging

from serial import SerialException
import serial_asyncio
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_VALUE_TEMPLATE, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

CONF_SERIAL_PORT = "serial_port"

DEFAULT_NAME = "Serial Sensor"
BAUDRATE = 19200

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SERIAL_PORT): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
    }
)


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
) -> None:
    name = config.get(CONF_NAME)
    port = config.get(CONF_SERIAL_PORT)

    sensor = SerialSensor(
        name,
        port,
        BAUDRATE,
    )

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, sensor.stop_serial_read)
    async_add_entities([sensor], True)


class SerialSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(
            self,
            name,
            port,
            baudrate,
    ):
        self._name = name
        self._state = None
        self._port = port
        self._baudrate = baudrate
        self._serial_loop_task = None

    async def async_added_to_hass(self) -> None:
        self._serial_loop_task = self.hass.loop.create_task(
            self.serial_read(
                self._port,
                self._baudrate,
            )
        )

    async def serial_read(
            self,
            device,
            baudrate,
    ):
        logged_error = False
        while True:
            try:
                reader, _ = await serial_asyncio.open_serial_connection(
                    url=device,
                    baudrate=baudrate
                )

            except SerialException:
                if not logged_error:
                    _LOGGER.exception(
                        "Unable to connect to the serial device %s. Will retry", device
                    )
                    logged_error = True
                await self._handle_error()
            else:
                _LOGGER.info("Serial device %s connected", device)
                while True:
                    try:
                        result = await reader.readexactly(26)
                    except SerialException:
                        _LOGGER.exception(
                            "Error while reading serial device %s", device
                        )
                        await self._handle_error()
                        break
                    else:
                        result = result.decode("utf-8").strip()
                        _LOGGER.debug("Received: %s", result)
                        self._state = result
                        self.async_write_ha_state()

    async def _handle_error(self):
        self._state = None
        self._attributes = None
        self.async_write_ha_state()
        await asyncio.sleep(5)

    @callback
    def stop_serial_read(self, event):
        if self._serial_loop_task:
            self._serial_loop_task.cancel()

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        return self._state
