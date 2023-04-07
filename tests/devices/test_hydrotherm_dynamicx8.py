from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_HIGH_DEMAND,
    STATE_HEAT_PUMP,
    STATE_OFF,
    STATE_PERFORMANCE,
    WaterHeaterEntityFeature,
)
from homeassistant.const import UnitOfTemperature

from ..const import HYDROTHERM_DYNAMICX8_PAYLOAD
from ..helpers import assert_device_properties_set
from ..mixins.binary_sensor import BasicBinarySensorTests
from .base_device_tests import TuyaDeviceTestCase

POWER_DP = "1"
TEMPERATURE_DP = "2"
CURRENTTEMP_DP = "3"
MODE_DP = "4"
ERROR_DP = "21"


class TestHydrothermDynamicX8(
    BasicBinarySensorTests,
    TuyaDeviceTestCase,
):
    __test__ = True

    def setUp(self):
        self.setUpForConfig(
            "hydrotherm_dynamic_x8_water_heater.yaml", HYDROTHERM_DYNAMICX8_PAYLOAD
        )
        self.subject = self.entities.get("water_heater")
        self.setUpBasicBinarySensor(
            ERROR_DP,
            self.entities.get("binary_sensor_fault"),
            device_class=BinarySensorDeviceClass.PROBLEM,
            testdata=(1, 0),
        )
        self.mark_secondary(["binary_sensor_fault"])

    def test_supported_features(self):
        self.assertEqual(
            self.subject.supported_features,
            WaterHeaterEntityFeature.OPERATION_MODE,
        )

    def test_temperature_unit_returns_celsius(self):
        self.assertEqual(self.subject.temperature_unit, UnitOfTemperature.CELSIUS)

    def test_current_temperature(self):
        self.dps[CURRENTTEMP_DP] = 55
        self.assertEqual(self.subject.current_temperature, 55)

    def test_target_temperature(self):
        self.dps[TEMPERATURE_DP] = 61
        self.assertEqual(self.subject.target_temperature, 61)

    def test_operation_list(self):
        self.assertCountEqual(
            self.subject.operation_list,
            [
                STATE_ECO,
                STATE_ELECTRIC,
                STATE_HEAT_PUMP,
                STATE_HIGH_DEMAND,
                STATE_PERFORMANCE,
                STATE_OFF,
            ],
        )

    def test_current_operation(self):
        self.dps[POWER_DP] = True
        self.dps[MODE_DP] = "ECO"
        self.assertEqual(self.subject.current_operation, STATE_ECO)
        self.dps[MODE_DP] = "STANDARD"
        self.assertEqual(self.subject.current_operation, STATE_HEAT_PUMP)
        self.dps[MODE_DP] = "HYBRID"
        self.assertEqual(self.subject.current_operation, STATE_HIGH_DEMAND)
        self.dps[MODE_DP] = "HYBRID1"
        self.assertEqual(self.subject.current_operation, STATE_PERFORMANCE)
        self.dps[MODE_DP] = "ELEMENT"
        self.assertEqual(self.subject.current_operation, STATE_ELECTRIC)
        self.dps[POWER_DP] = False
        self.assertEqual(self.subject.current_operation, STATE_OFF)

    async def test_set_temperature_fails(self):
        with self.assertRaises(TypeError):
            await self.subject.async_set_temperature(temperature=65)

    async def test_set_operation_mode_to_eco(self):
        async with assert_device_properties_set(
            self.subject._device,
            {POWER_DP: True, MODE_DP: "ECO"},
        ):
            await self.subject.async_set_operation_mode(STATE_ECO)

    async def test_set_operation_mode_to_heat_pump(self):
        async with assert_device_properties_set(
            self.subject._device,
            {POWER_DP: True, MODE_DP: "STANDARD"},
        ):
            await self.subject.async_set_operation_mode(STATE_HEAT_PUMP)

    async def test_set_operation_mode_to_electric(self):
        async with assert_device_properties_set(
            self.subject._device,
            {POWER_DP: True, MODE_DP: "ELEMENT"},
        ):
            await self.subject.async_set_operation_mode(STATE_ELECTRIC)

    async def test_set_operation_mode_to_highdemand(self):
        async with assert_device_properties_set(
            self.subject._device,
            {POWER_DP: True, MODE_DP: "HYBRID"},
        ):
            await self.subject.async_set_operation_mode(STATE_HIGH_DEMAND)

    async def test_set_operation_mode_to_performance(self):
        async with assert_device_properties_set(
            self.subject._device,
            {POWER_DP: True, MODE_DP: "HYBRID1"},
        ):
            await self.subject.async_set_operation_mode(STATE_PERFORMANCE)

    async def test_set_operation_mode_to_off(self):
        async with assert_device_properties_set(
            self.subject._device,
            {POWER_DP: False},
        ):
            await self.subject.async_set_operation_mode(STATE_OFF)
