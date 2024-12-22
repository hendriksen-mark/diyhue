import logManager
import configManager
import socket
import json
import uuid
from datetime import datetime, timezone
from lights.protocols import tpkasa, wled, mqtt, hyperion, yeelight, hue, deconz, native_multi, tasmota, shelly, esphome, tradfri, elgato
from services import homeAssistantWS
from HueObjects import Light, StreamEvent
from functions.core import nextFreeId
from lights.light_types import lightTypes

logging = logManager.logger.get_logger(__name__)
bridgeConfig = configManager.bridgeConfig.yaml_config

def pretty_json(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

def scanHost(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.02)
        return sock.connect_ex((host, port))

def iter_ips(port):
    rangeConfig = bridgeConfig["config"]["IP_RANGE"]
    HOST_IP = configManager.runtimeConfig.arg["HOST_IP"]
    scan_on_host_ip = bridgeConfig["config"]["scanonhostip"]
    ip_range_start = rangeConfig["IP_RANGE_START"]
    ip_range_end = rangeConfig["IP_RANGE_END"]
    sub_ip_range_start = rangeConfig["SUB_IP_RANGE_START"]
    sub_ip_range_end = rangeConfig["SUB_IP_RANGE_END"]
    host = HOST_IP.split('.')
    if scan_on_host_ip:
        yield ('127.0.0.1', port)
    for sub_addr in range(sub_ip_range_start, sub_ip_range_end + 1):
        host[2] = str(sub_addr)
        for addr in range(ip_range_start, ip_range_end + 1):
            host[3] = str(addr)
            test_host = '.'.join(host)
            if test_host != HOST_IP:
                yield (test_host, port)

def find_hosts(port):
    return [f'{host}:{port}' for host, port in iter_ips(port) if scanHost(host, port) == 0]

def addNewLight(modelid, name, protocol, protocol_cfg):
    newLightID = nextFreeId(bridgeConfig, "lights")
    if modelid in lightTypes:
        light = lightTypes[modelid]
        light.update({
            "name": name,
            "id_v1": newLightID,
            "modelid": modelid,
            "protocol": protocol,
            "protocol_cfg": protocol_cfg
        })
        newObject = Light.Light(light)
        bridgeConfig["lights"][newLightID] = newObject
        bridgeConfig["groups"]["0"].add_light(newObject)
        rooms = [obj.id_v2 for obj in bridgeConfig["groups"].values()]
        lights = [obj.id_v2 for obj in bridgeConfig["lights"].values()]
        bridgeConfig["groups"]["0"].groupZeroStream(rooms, lights)
        configManager.bridgeConfig.save_config(backup=False, resource="lights")
        return newLightID
    return False

def manualAddLight(ip, protocol, config={}):
    modelid = config.get("lightModelID", "LCT015")
    name = config.get("lightName", "New Light")
    if protocol == "auto":
        detectedLights = []
        for discover_func in [native_multi.discover, tasmota.discover, shelly.discover, esphome.discover]:
            discover_func(detectedLights, [ip])
        for light in detectedLights:
            logging.info(f"Found light {light['protocol']} {light['name']}")
            addNewLight(light["modelid"], light["name"], light["protocol"], light["protocol_cfg"])
    else:
        config["ip"] = ip
        addNewLight(modelid, name, protocol, config)

def discoveryEvent():
    streamMessage = {
        "creationtime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": [{
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, bridgeConfig["config"]["bridgeid"] + 'zigbee_device_discovery')),
            "owner": {
                "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, bridgeConfig["config"]["bridgeid"] + 'device')),
                "rtype": "device"
            },
            "status": bridgeConfig["config"]["zigbee_device_discovery_info"]["status"],
            "type": "zigbee_device_discovery"
        }],
        "id": str(uuid.uuid4()),
        "type": "update"
    }
    StreamEvent(streamMessage)

def update_light_ip(lightObj, light):
    logging.info(f"Update IP for light {light['name']}")
    lightObj.protocol_cfg.update(light["protocol_cfg"])

def is_light_matching(lightObj, light):
    protocol = light["protocol"]
    if protocol == "native_multi":
        return (lightObj.protocol_cfg["mac"] == light["protocol_cfg"]["mac"] and
                lightObj.protocol_cfg["light_nr"] == light["protocol_cfg"]["light_nr"] and
                lightObj.modelid == light["modelid"])
    if protocol in ["yeelight", "tasmota", "tradfri", "hyperion", "tpkasa"]:
        return lightObj.protocol_cfg["id"] == light["protocol_cfg"]["id"] and lightObj.modelid == light["modelid"]
    if protocol in ["shelly", "native", "native_single", "esphome", "elgato"]:
        return lightObj.protocol_cfg["mac"] == light["protocol_cfg"]["mac"] and lightObj.modelid == light["modelid"]
    if protocol in ["hue", "deconz"]:
        return lightObj.protocol_cfg["uniqueid"] == light["protocol_cfg"]["uniqueid"] and lightObj.modelid == light["modelid"]
    if protocol == "wled":
        return (lightObj.protocol_cfg["mac"] == light["protocol_cfg"]["mac"] and
                lightObj.protocol_cfg["segmentId"] == light["protocol_cfg"]["segmentId"] and
                lightObj.modelid == light["modelid"])
    if protocol == "homeassistant_ws":
        return lightObj.protocol_cfg["entity_id"] == light["protocol_cfg"]["entity_id"] and lightObj.modelid == light["modelid"]
    return False

def get_device_ips():
    if bridgeConfig["config"]["port"]["enabled"]:
        return [host for ports in bridgeConfig["config"]["port"]["ports"] for host in find_hosts(ports)]
    return find_hosts(80)

def discover_lights(detectedLights, device_ips):
    if bridgeConfig["config"]["mqtt"]["enabled"]:
        # brioadcast MQTT message, lights will be added by the service
        mqtt.discover(bridgeConfig["config"]["mqtt"])
    if bridgeConfig["config"]["deconz"]["enabled"]:
        deconz.discover(detectedLights, bridgeConfig["config"]["deconz"])
    if bridgeConfig["config"]["homeassistant"]["enabled"]:
        homeAssistantWS.discover(detectedLights)
    if bridgeConfig["config"]["yeelight"]["enabled"]:
        yeelight.discover(detectedLights)
    # native_multi probe all esp8266 lights with firmware from diyhue repo
    if bridgeConfig["config"]["native_multi"]["enabled"]:
        native_multi.discover(detectedLights, device_ips)
    if bridgeConfig["config"]["tasmota"]["enabled"]:
        tasmota.discover(detectedLights, device_ips)
    if bridgeConfig["config"]["wled"]["enabled"]:
        # Most of the other discoveries are disabled by having no IP address (--disable-network-scan)
        # But wled does an mdns discovery as well.
        wled.discover(detectedLights, device_ips)
    if bridgeConfig["config"]["hue"]:
        hue.discover(detectedLights, bridgeConfig["config"]["hue"])
    if bridgeConfig["config"]["shelly"]["enabled"]:
        shelly.discover(detectedLights, device_ips)
    if bridgeConfig["config"]["esphome"]["enabled"]:
        esphome.discover(detectedLights, device_ips)
    if bridgeConfig["config"]["tradfri"]:
        tradfri.discover(detectedLights, bridgeConfig["config"]["tradfri"])
    if bridgeConfig["config"]["hyperion"]["enabled"]:
        hyperion.discover(detectedLights)
    if bridgeConfig["config"]["tpkasa"]["enabled"]:
        tpkasa.discover(detectedLights)
    if bridgeConfig["config"]["elgato"]["enabled"]:
        # Scan with port 9123 before mDNS discovery
        elgato_ips = find_hosts(9123)
        logging.info(pretty_json(elgato_ips))
        elgato.discover(detectedLights, elgato_ips)

def scanForLights():  # scan for ESP8266 lights and strips
    logging.info("scan for light")
    bridgeConfig["temp"]["scanResult"] = {"lastscan": "active"}
    bridgeConfig["config"]["zigbee_device_discovery_info"]["status"] = "active"
    discoveryEvent()
    detectedLights = []
    device_ips = get_device_ips()
    logging.info(pretty_json(device_ips))
    discover_lights(detectedLights, device_ips)
    bridgeConfig["temp"]["scanResult"]["lastscan"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    for light in detectedLights:
        lightIsNew = True
        for lightObj in bridgeConfig["lights"].values():
            if lightObj.protocol == light["protocol"] and is_light_matching(lightObj, light):
                update_light_ip(lightObj, light)
                lightIsNew = False
                break
        if lightIsNew:
            logging.info(f"Add new light {light['name']}")
            lightId = addNewLight(light["modelid"], light["name"], light["protocol"], light["protocol_cfg"])
            bridgeConfig["temp"]["scanResult"][lightId] = {"name": light["name"]}
    bridgeConfig["config"]["zigbee_device_discovery_info"]["status"] = "ready"
    discoveryEvent()
    return bridgeConfig["temp"]["scanResult"]
