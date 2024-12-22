import json
import logManager
import requests
from typing import Dict, List, Any

logging = logManager.logger.get_logger(__name__)

def set_light(light, data):
    lightsData = data.get("lights", {light.protocol_cfg["light_nr"]: data})
    try:
        response = requests.put(f"http://{light.protocol_cfg['ip']}/state", json=lightsData, timeout=3)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to set light state: {e}")
        return str(e)

def get_light_state(light):
    try:
        response = requests.get(f"http://{light.protocol_cfg['ip']}/state?light={light.protocol_cfg['light_nr']}", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to get light state: {e}")
        return {}

def generate_light_name(base_name, light_nr):
    suffix = f' {light_nr}'
    return f'{base_name[:32-len(suffix)]}{suffix}'

def is_json(content):
    try:
        json.loads(content)
    except ValueError:
        return False
    return True

def discover(detectedLights, device_ips):
    logging.debug("native: <discover> invoked!")
    for ip in device_ips:
        try:
            response = requests.get(f"http://{ip}/detect", timeout=3)
            response.raise_for_status()
            if response.content and is_json(response.content):  # Check if response content is valid JSON
                device_data = response.json()
                logging.debug(json.dumps(device_data))

                if "modelid" in device_data:
                    logging.info(f"{ip} is {device_data['name']}")
                    protocol = device_data.get("protocol", "native")
                    lights = device_data.get("lights", 1)

                    logging.info(f"Detected light : {device_data['name']}")
                    for x in range(1, lights + 1):
                        lightName = generate_light_name(device_data['name'], x)
                        protocol_cfg = {
                            "ip": ip,
                            "version": device_data["version"],
                            "type": device_data["type"],
                            "light_nr": x,
                            "mac": device_data["mac"]
                        }
                        if device_data["modelid"] in ["LCX002", "915005987201", "LCX004"]:
                            protocol_cfg["points_capable"] = 5
                        detectedLights.append({
                            "protocol": protocol,
                            "name": lightName,
                            "modelid": device_data["modelid"],
                            "protocol_cfg": protocol_cfg
                        })
            else:
                logging.info(f"ip {ip} returned empty or invalid JSON response")

        except requests.RequestException as e:
            logging.info(f"ip {ip} is unknown device: {e}")

    return detectedLights
