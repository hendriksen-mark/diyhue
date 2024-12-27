import logManager
import requests
from typing import Any, Dict

logging = logManager.logger.get_logger(__name__)

def set_light(light: Any, data: Dict[str, Any]) -> str:
    """
    Set the state of the light.

    Args:
        light (Any): The light object containing protocol configuration.
        data (Dict[str, Any]): The state data to be sent to the light.

    Returns:
        str: The response text from the light.
    """
    state = requests.put(f'http://{light.protocol_cfg["ip"]}/state', json=data, timeout=3)
    return state.text

def get_light_state(light: Any) -> Dict[str, Any]:
    """
    Get the current state of the light.

    Args:
        light (Any): The light object containing protocol configuration.

    Returns:
        Dict[str, Any]: The current state of the light.
    """
    state = requests.get(f'http://{light.protocol_cfg["ip"]}/state', timeout=3)
    return state.json()
