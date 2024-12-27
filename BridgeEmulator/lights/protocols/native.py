import requests
from typing import Dict, Any

def set_light(light: Any, data: Dict[str, Any]) -> None:
    """
    Set the state of the light.

    Args:
        light (Any): The light object containing protocol configuration.
        data (Dict[str, Any]): The data to set on the light.
    """
    url = "http://" + light.protocol_cfg["ip"] + "/set?light=" + str(light.protocol_cfg["light_nr"])
    method = 'GET'
    for key, value in data.items():
        if key == "xy":
            url += "&x=" + str(value[0]) + "&y=" + str(value[1])
        else:
            url += "&" + key + "=" + str(value)
    requests.get(url, timeout=3)

def get_light_state(light: Any) -> Dict[str, Any]:
    """
    Get the current state of the light.

    Args:
        light (Any): The light object containing protocol configuration.

    Returns:
        Dict[str, Any]: The current state of the light.
    """
    state = requests.get("http://"+light.protocol_cfg["ip"]+"/get?light=" + str(light.protocol_cfg["light_nr"]), timeout=3)
    return state.json()

