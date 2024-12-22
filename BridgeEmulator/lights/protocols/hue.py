import json
import logManager
import requests

logging = logManager.logger.get_logger(__name__)

def build_url(light, endpoint="state"):
    return f"http://{light.protocol_cfg['ip']}/api/{light.protocol_cfg['hueUser']}/lights/{light.protocol_cfg['id']}/{endpoint}"

def set_light(light, data):
    url = build_url(light)
    payload = {}
    payload.update(data)
    color = {}
    if "xy" in payload:
        color["xy"] = payload["xy"]
        del(payload["xy"])
    elif "ct" in payload:
        color["ct"] = payload["ct"]
        del(payload["ct"])
    elif "hue" in payload:
        color["hue"] = payload["hue"]
        del(payload["hue"])
    elif "sat" in payload:
        color["sat"] = payload["sat"]
        del(payload["sat"])
    if payload:
        requests.put(url, json=payload, timeout=3)
    if color:
        requests.put(url, json=color, timeout=3)

def get_light_state(light):
    try:
        state = requests.get(build_url(light, ""), timeout=3)
        state.raise_for_status()
        return state.json()["state"]
    except requests.RequestException as e:
        logging.error("Error getting light state: %s", e)
        return None

def discover(detectedLights, credentials):
    if "hueUser" in credentials and len(credentials["hueUser"]) >= 32:
        logging.debug("hue: <discover> invoked!")
        try:
            response = requests.get(f"http://{credentials['ip']}/api/{credentials['hueUser']}/lights", timeout=3)
            response.raise_for_status()
            lights = response.json()
            for id, light in lights.items():
                modelid = "LCT015"
                if light["type"] == "Dimmable light":
                    modelid = "LWB010"
                elif light["type"] == "Color temperature light":
                    modelid = "LTW001"
                elif light["type"] == "On/Off plug-in unit":
                    modelid = "LOM001"
                elif light["type"] == "Color light":
                    modelid = "LLC010"
                detectedLights.append({
                    "protocol": "hue", 
                    "name": light["name"], 
                    "modelid": modelid, 
                    "protocol_cfg": {
                        "ip": credentials["ip"], 
                        "hueUser": credentials["hueUser"], 
                        "modelid": light["modelid"], 
                        "id": id, 
                        "uniqueid": light["uniqueid"]
                    }
                })
        except requests.RequestException as e:
            logging.error("Error connecting to Hue Bridge: %s", e)
