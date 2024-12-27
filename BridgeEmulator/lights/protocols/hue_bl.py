import logManager
from functions.colors import convert_xy
import asyncio
from typing import Dict, Tuple, Optional
logging = logManager.logger.get_logger(__name__)
Connections: Dict[str, 'Lamp'] = {}

### libhueble ###
### https://github.com/alexhorn/libhueble/ ###
from bleak import BleakClient
from rgbxy import Converter, GamutC, get_light_gamut
from struct import pack, unpack

# model number as an ASCII string
CHAR_MODEL = '00002a24-0000-1000-8000-00805f9b34fb'
# power state (0 or 1)
CHAR_POWER = '932c32bd-0002-47a2-835a-a8d455b859dd'
# brightness (1 to 254)
CHAR_BRIGHTNESS = '932c32bd-0003-47a2-835a-a8d455b859dd'
# color (CIE XY coordinates converted to two 16-bit little-endian integers)
CHAR_COLOR = '932c32bd-0005-47a2-835a-a8d455b859dd'

class Lamp(object):
    """A wrapper for the Philips Hue BLE protocol"""

    def __init__(self, address: str):
        """
        Initialize the Lamp object.

        Args:
            address (str): The BLE address of the lamp.
        """
        self.address = address
        self.client: Optional[BleakClient] = None

    @property
    def is_connected(self) -> bool:
        """
        Check if the client is connected.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.client is not None and self.client.is_connected

    async def connect(self) -> None:
        """
        Connect to the BLE lamp.
        """
        self.client = BleakClient(self.address)
        try:
            await self.client.connect()
            logging.info(f"Connected to {self.address}")
            model = await self.get_model()
            try:
                self.converter = Converter(get_light_gamut(model))
            except ValueError:
                self.converter = Converter(GamutC)
        except Exception as e:
            logging.error(f"Failed to connect to {self.address}: {e}")
            self.client = None

    async def disconnect(self) -> None:
        """
        Disconnect from the BLE lamp.
        """
        if self.client:
            await self.client.disconnect()
            logging.info(f"Disconnected from {self.address}")
            self.client = None

    async def get_model(self) -> str:
        """
        Get the model string of the lamp.

        Returns:
            str: The model string.
        """
        model = await self.client.read_gatt_char(CHAR_MODEL)
        return model.decode('ascii')

    async def get_power(self) -> bool:
        """
        Get the current power state of the lamp.

        Returns:
            bool: True if the lamp is on, False otherwise.
        """
        power = await self.client.read_gatt_char(CHAR_POWER)
        return bool(power[0])

    async def set_power(self, on: bool) -> None:
        """
        Set the power state of the lamp.

        Args:
            on (bool): True to turn on, False to turn off.
        """
        await self.client.write_gatt_char(CHAR_POWER, bytes([1 if on else 0]), response=True)

    async def get_brightness(self) -> float:
        """
        Get the current brightness of the lamp.

        Returns:
            float: Brightness as a float between 0.0 and 1.0.
        """
        brightness = await self.client.read_gatt_char(CHAR_BRIGHTNESS)
        return brightness[0] / 255

    async def set_brightness(self, brightness: float) -> None:
        """
        Set the brightness of the lamp.

        Args:
            brightness (float): Brightness as a float between 0.0 and 1.0.
        """
        await self.client.write_gatt_char(CHAR_BRIGHTNESS, bytes([max(min(int(brightness * 255), 254), 1)]), response=True)

    async def get_color_xy(self) -> Tuple[float, float]:
        """
        Get the current XY color coordinates of the lamp.

        Returns:
            Tuple[float, float]: A tuple of X and Y coordinates as floats between 0.0 and 1.0.
        """
        buf = await self.client.read_gatt_char(CHAR_COLOR)
        x, y = unpack('<HH', buf)
        return x / 0xFFFF, y / 0xFFFF

    async def set_color_xy(self, x: float, y: float) -> None:
        """
        Set the XY color coordinates of the lamp.

        Args:
            x (float): X coordinate as a float between 0.0 and 1.0.
            y (float): Y coordinate as a float between 0.0 and 1.0.
        """
        buf = pack('<HH', int(x * 0xFFFF), int(y * 0xFFFF))
        await self.client.write_gatt_char(CHAR_COLOR, buf, response=True)

    async def get_color_rgb(self) -> Tuple[float, float, float]:
        """
        Get the RGB color of the lamp.

        Returns:
            Tuple[float, float, float]: A tuple of R, G, and B values as floats between 0.0 and 1.0.
        """
        x, y = await self.get_color_xy()
        return self.converter.xy_to_rgb(x, y)

    async def set_color_rgb(self, r: float, g: float, b: float) -> None:
        """
        Set the RGB color of the lamp.

        Args:
            r (float): Red value as a float between 0.0 and 1.0.
            g (float): Green value as a float between 0.0 and 1.0.
            b (float): Blue value as a float between 0.0 and 1.0.
        """
        x, y = self.converter.rgb_to_xy(r, g, b)
        await self.set_color_xy(x, y)

def connect(light) -> Lamp:
    """
    Connect to the lamp.

    Args:
        light: The light object containing protocol configuration.

    Returns:
        Lamp: The connected Lamp object.
    """
    ip = light.protocol_cfg["ip"]
    if ip in Connections:
        c = Connections[ip]
    else:
        c = Lamp(ip)
        asyncio.run(c.connect())
        Connections[ip] = c
    return c

def set_light(light, data: Dict[str, any]) -> None:
    """
    Set the light properties.

    Args:
        light: The light object.
        data (Dict[str, any]): A dictionary containing the light properties to set.
    """
    c = connect(light)
    for key, value in data.items():
        if key == "on":
            asyncio.run(c.set_power(value))
        if key == "bri":
            asyncio.run(c.set_brightness(value / 254))
        if key == "xy":
            color = convert_xy(value[0], value[1], light.state["bri"])
            asyncio.run(c.set_color_rgb(color[0] / 254, color[1] / 254, color[2] / 254))
