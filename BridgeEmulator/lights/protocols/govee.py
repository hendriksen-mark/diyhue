import json
import requests
import logManager
from functions.colors import convert_rgb_xy, convert_xy, hsv_to_rgb, rgbBrightness
import configManager

logging = logManager.logger.get_logger(__name__)
bridgeConfig = configManager.bridgeConfig.yaml_config

API_KEY = bridgeConfig["config"]["govee"]["api_key"]
BASE_URL = "https://openapi.api.govee.com/router/api/v1/"

def get_headers():
    return {
        "Govee-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

def discover(detectedLights):
    logging.debug("Govee: <discover> invoked!")
    response = requests.get(f"{BASE_URL}/devices", headers=get_headers())
    response.raise_for_status()
    devices = response.json().get("data", {}).get("devices", [])
    for device in devices:
        model = device["model"]
        device_name = device["deviceName"]
        device_id = device["device"]
        properties = {
            "device_id": device_id,
            "model": model,
            "name": device_name
        }
        detectedLights.append({"protocol": "govee", "name": device_name, "modelid": model, "protocol_cfg": properties})
        logging.debug(f"Govee: Found {device_name} with model {model}")

def set_light(light, data):
    logging.debug(f"Govee: <set_light> invoked! Device ID={light.protocol_cfg['device_id']}")
    device_id = light.protocol_cfg["device_id"]
    model = light.protocol_cfg["model"]
    request_data = {"device": device_id, "model": model, "cmd": {"name": "turn", "value": "off" if "on" in data and not data['on'] else "on"}}

    if "bri" in data:
        brightness = data['bri']
        request_data["cmd"] = {"name": "brightness", "value": brightness}

    if "xy" in data:
        color = convert_xy(data['xy'][0], data['xy'][1], data.get('bri', 255))
        request_data["cmd"] = {"name": "color", "value": {"r": color[0], "g": color[1], "b": color[2]}}

    if "ct" in data:
        request_data["cmd"] = {"name": "colorTem", "value": data['ct']}

    if "hue" in data or "sat" in data:
        hue = data.get('hue', 0)
        sat = data.get('sat', 0)
        bri = data.get('bri', 255)
        color = hsv_to_rgb(hue, sat, bri)
        request_data["cmd"] = {"name": "color", "value": {"r": color[0], "g": color[1], "b": color[2]}}

    response = requests.put(f"{BASE_URL}/device/control", headers=get_headers(), data=json.dumps(request_data))
    response.raise_for_status()

def get_light_state(light):
    logging.debug("Govee: <get_light_state> invoked!")
    device_id = light.protocol_cfg["device_id"]
    response = requests.get(f"{BASE_URL}/device/state?device={device_id}", headers=get_headers())
    response.raise_for_status()
    state_data = response.json().get("data", {}).get("properties", {})
    state = {"on": state_data.get("powerState", "off") == "on"}
    if "brightness" in state_data:
        state["bri"] = state_data["brightness"]
    if "color" in state_data:
        color = state_data["color"]
        state["xy"] = convert_rgb_xy(color["r"], color["g"], color["b"])
    if "colorTem" in state_data:
        state["ct"] = state_data["colorTem"]
    return state
