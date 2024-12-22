import json
import math
import ssl
import weakref
from datetime import datetime, timezone
from threading import Thread
from time import sleep
from typing import Any, Dict, Optional, Union

import paho.mqtt.client as mqtt
import requests

import configManager
import logManager
from HueObjects import Sensor
from functions.behavior_instance import checkBehaviorInstances
from functions.core import nextFreeId
from functions.rules import rulesProcessor
from lights.discover import addNewLight
from sensors.discover import addHueMotionSensor
from sensors.sensor_types import sensorTypes

logging = logManager.logger.get_logger(__name__)
bridgeConfig = configManager.bridgeConfig.yaml_config
client = mqtt.Client()

devices_ids: Dict[str, weakref.ReferenceType] = {}

# Configuration stuff
discoveryPrefix = "homeassistant"
latestStates: Dict[str, Any] = {}
discoveredDevices: Dict[str, Any] = {}

motionSensors = ["TRADFRI motion sensor", "lumi.sensor_motion.aq2", "lumi.sensor_motion", "lumi.motion.ac02", "SML001"]
standardSensors = {
    "TRADFRI remote control": {
        "dataConversion": {
            "rootKey": "action",
            "toggle": {"buttonevent": 1002},
            "arrow_right_click": {"buttonevent": 5002},
            "arrow_right_hold": {"buttonevent": 5001},
            "arrow_left_click": {"buttonevent": 4002},
            "arrow_left_hold": {"buttonevent": 4001},
            "brightness_up_click": {"buttonevent": 2002},
            "brightness_up_hold": {"buttonevent": 2001},
            "brightness_down_click": {"buttonevent": 3002},
            "brightness_down_hold": {"buttonevent": 3001},
            "brightness_up_release": {"buttonevent": 2003},
            "brightness_down_release": {"buttonevent": 3003},
            "arrow_left_release": {"buttonevent": 4003},
            "arrow_right_release": {"buttonevent": 5003},
        }
    },
    "TRADFRI on/off switch": {
        "dataConversion": {
            "rootKey": "action",
            "on": {"buttonevent": 1002},
            "off": {"buttonevent": 2002},
            "brightness_up": {"buttonevent": 1001},
            "brightness_down": {"buttonevent": 2001},
            "brightness_stop": {"buttonevent": 3001},
        }
    },
    "TRADFRI wireless dimmer": {
        "dataConversion": {
            "rootKey": "action",
            "rotate_right_quick": {"buttonevent": 1002},
            "rotate_right": {"buttonevent": 2002},
            "rotate_left": {"buttonevent": 3002},
            "rotate_left_quick": {"buttonevent": 4002},
            "rotate_stop": {},
            "": {},
        }
    },
    "RWL021": {
        "dataConversion": {
            "rootKey": "action",
            "on_press": {"buttonevent": 1000},
            "on-press": {"buttonevent": 1000},
            "on_hold": {"buttonevent": 1001},
            "on-hold": {"buttonevent": 1001},
            "on_press_release": {"buttonevent": 1002},
            "on-press-release": {"buttonevent": 1002},
            "on_hold_release": {"buttonevent": 1003},
            "on-hold-release": {"buttonevent": 1003},
            "up_press": {"buttonevent": 2000},
            "up-press": {"buttonevent": 2000},
            "up_hold": {"buttonevent": 2001},
            "up-hold": {"buttonevent": 2001},
            "up_press_release": {"buttonevent": 2002},
            "up-press-release": {"buttonevent": 2002},
            "up_hold_release": {"buttonevent": 2003},
            "up-hold-release": {"buttonevent": 2003},
            "down_press": {"buttonevent": 3000},
            "down-press": {"buttonevent": 3000},
            "down_hold": {"buttonevent": 3001},
            "down-hold": {"buttonevent": 3001},
            "down_press_release": {"buttonevent": 3002},
            "down-press-release": {"buttonevent": 3002},
            "down_hold_release": {"buttonevent": 3003},
            "down-hold-release": {"buttonevent": 3003},
            "off_press": {"buttonevent": 4000},
            "off-press": {"buttonevent": 4000},
            "off_hold": {"buttonevent": 4001},
            "off-hold": {"buttonevent": 4001},
            "off_press_release": {"buttonevent": 4002},
            "off-press-release": {"buttonevent": 4002},
            "off_hold_release": {"buttonevent": 4003},
            "off-hold-release": {"buttonevent": 4003},
        }
    },
    "WXKG01LM": {
        "dataConversion": {
            "rootKey": "action",
            "single": {"buttonevent": 1001},
            "double": {"buttonevent": 1002},
            "triple": {"buttonevent": 1003},
            "quadruple": {"buttonevent": 1004},
            "hold": {"buttonevent": 2001},
            "release": {"buttonevent": 2002},
            "release": {"many": 2003},
        }
    },
    "Remote Control N2": {
        "dataConversion": {
            "rootKey": "action",
            "on": {"buttonevent": 1001},
            "off": {"buttonevent": 2001},
            "brightness_move_up": {"buttonevent": 1002},
            "brightness_stop": {"buttonevent": 1003},
            "brightness_move_down": {"buttonevent": 2002},
            "arrow_left_click": {"buttonevent": 3002},
            "arrow_right_click": {"many": 4002},
        }
    },
    "RDM002": {
        "dataConversion": {
            "rootKey": "action",
            "dirKey": "action_direction",
            "typeKey": "action_type",
            "timeKey": "action_time",
            "button_1_press": {"buttonevent": 1000},
            "button_1_hold": {"buttonevent": 1001},
            "button_1_press_release": {"buttonevent": 1002},
            "button_1_hold_release": {"buttonevent": 1003},
            "button_2_press": {"buttonevent": 2000},
            "button_2_hold": {"buttonevent": 2001},
            "button_2_press_release": {"buttonevent": 2002},
            "button_2_hold_release": {"buttonevent": 2003},
            "button_3_press": {"buttonevent": 3000},
            "button_3_hold": {"buttonevent": 3001},
            "button_3_press_release": {"buttonevent": 3002},
            "button_3_hold_release": {"buttonevent": 3003},
            "button_4_press": {"buttonevent": 4000},
            "button_4_hold": {"buttonevent": 4001},
            "button_4_press_release": {"buttonevent": 4002},
            "button_4_hold_release": {"buttonevent": 4003},
            "dial_rotate_left_step": {"rotaryevent": 1},
            "dial_rotate_left_slow": {"rotaryevent": 2},
            "dial_rotate_left_fast": {"rotaryevent": 2},
            "dial_rotate_right_step": {"rotaryevent": 1},
            "dial_rotate_right_slow": {"rotaryevent": 2},
            "dial_rotate_right_fast": {"rotaryevent": 2},
            "expectedrotation":90,
            "expectedeventduration":400
        }
    },
    "PTM 215Z": {
        "dataConversion": {
            "rootKey": "action",
            "press_1": {"buttonevent": 1000},
            "release_1": {"buttonevent": 1002},
            "press_2": {"buttonevent": 2000},
            "release_2": {"buttonevent": 2002},
            "press_3": {"buttonevent": 3000},
            "release_3": {"buttonevent": 3002},
            "press_4": {"buttonevent": 4000},
            "release_4": {"buttonevent": 4002},
            "press_1_and_3": {"buttonevent": 1010},
            "release_1_and_3": {"buttonevent": 1003},
            "press_2_and_4": {"buttonevent": 2010},
            "release_2_and_4": {"buttonevent": 2003},
            "press_energy_bar": {"buttonevent": 5000},
        }
    },
}

# WXKG01LM MiJia wireless switch https://www.zigbee2mqtt.io/devices/WXKG01LM.html
standardSensors["RWL020"] = standardSensors["RWL021"]
standardSensors["RWL022"] = standardSensors["RWL021"]
standardSensors["8719514440937"] = standardSensors["RDM002"]
standardSensors["8719514440999"] = standardSensors["RDM002"]
standardSensors["9290035001"] = standardSensors["RDM002"]
standardSensors["9290035003"] = standardSensors["RDM002"]

def getClient() -> mqtt.Client:
    """Returns the MQTT client instance."""
    return client

def longPressButton(sensor: Sensor, buttonevent: int) -> None:
    """Handles long press button events."""
    logging.info("Long press detected")
    sleep(1)
    while sensor.state["buttonevent"] == buttonevent:
        logging.info("Still pressed")
        current_time = datetime.now()
        sensor.dxState["lastupdated"] = current_time
        rulesProcessor(sensor, current_time)
        checkBehaviorInstances(sensor)
        sleep(0.5)

def streamGroupEvent(device: Sensor, state: Dict[str, Any]) -> None:
    """Streams group events for a device."""
    for id, group in bridgeConfig["groups"].items():
        if id != "0":
            for light in group.lights:
                if light().id_v1 == device.id_v1:
                    group.genStreamEvent(state)

def getObject(friendly_name: str) -> Union[Sensor.Sensor, bool]:
    """Retrieves an object by its friendly name."""
    if friendly_name in devices_ids:
        logging.debug("Cache Hit for " + friendly_name)
        return devices_ids[friendly_name]()
    else:
        for resource in ["sensors", "lights"]:
            for key, device in bridgeConfig[resource].items():
                if device.protocol == "mqtt":
                    if "friendly_name" in device.protocol_cfg and device.protocol_cfg["friendly_name"] == friendly_name:
                        if device.modelid == "SML001" and device.type != "ZLLPresence":
                            continue
                        devices_ids[friendly_name] = weakref.ref(device)
                        logging.debug("Cache Miss " + friendly_name)
                        return device
                    elif "state_topic" in device.protocol_cfg and device.protocol_cfg["state_topic"] == "zigbee2mqtt/" + friendly_name:
                        devices_ids[friendly_name] = weakref.ref(device)
                        logging.debug("Cache Miss " + friendly_name)
                        return device
        logging.debug("Device not found for " + friendly_name)
        return False

def on_autodiscovery_light(msg: mqtt.MQTTMessage) -> None:
    """Handles auto-discovery messages for lights."""
    data = json.loads(msg.payload)
    logging.info("Auto discovery message on: " + msg.topic)
    discoveredDevices[data['unique_id']] = data
    for key, data in discoveredDevices.items():
        device_new = True
        for light, obj in bridgeConfig["lights"].items():
            if obj.protocol == "mqtt" and obj.protocol_cfg["uid"] == key:
                device_new = False
                obj.protocol_cfg["command_topic"] = data["command_topic"]
                obj.protocol_cfg["state_topic"] = data["state_topic"]
                break

        if device_new:
            lightName = data["device"]["name"] if data["device"]["name"] is not None else data["name"]
            logging.debug("MQTT: Adding light " + lightName)

            # Device capabilities
            keys = data.keys()
            light_xy = "xy" in keys and data["xy"] == True
            light_brightness = "brightness" in keys and data["brightness"] == True
            light_ct = "color_temp" in keys and data["color_temp"] == True

            modelid = None
            if light_xy and light_ct:
                modelid = "LCT015"
            elif light_xy and not light_ct:
                modelid = "LLC010"
            elif light_xy:
                modelid = "LCT001"
            elif light_ct:
                modelid = "LTW001"
            elif light_brightness:
                modelid = "LWB010"
            else:
                modelid = "LOM001"
            protocol_cfg = {
                "uid": data["unique_id"],
                "ip": "mqtt",
                "state_topic": data["state_topic"],
                "command_topic": data["command_topic"],
                "mqtt_server": bridgeConfig["config"]["mqtt"]
            }

            addNewLight(modelid, lightName, "mqtt", protocol_cfg)

def on_state_update(msg: mqtt.MQTTMessage) -> None:
    """Handles state update messages."""
    logging.debug("MQTT: got state message on " + msg.topic)
    data = json.loads(msg.payload)
    latestStates[msg.topic] = data
    logging.debug(json.dumps(data, indent=4))

def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
    """Handles incoming MQTT messages."""
    if bridgeConfig["config"]["mqtt"]["enabled"]:
        try:
            current_time = datetime.now()
            logging.debug("MQTT: got state message on " + msg.topic)
            data = json.loads(msg.payload)
            logging.debug(msg.payload)
            if msg.topic.startswith(discoveryPrefix + "/light/"):
                on_autodiscovery_light(msg)
            elif msg.topic == "zigbee2mqtt/bridge/devices":
                for key in data:
                    if "model_id" in key and (key["model_id"] in standardSensors or key["model_id"] in motionSensors):
                        if not getObject(key["friendly_name"]):
                            logging.info("MQTT: Add new mqtt sensor " + key["friendly_name"])
                            if key["model_id"] in standardSensors:
                                for sensor_type in sensorTypes[key["model_id"]].keys():
                                    new_sensor_id = nextFreeId(bridgeConfig, "sensors")
                                    uniqueid = convertHexToMac(key["ieee_address"]) + "-01-1000"
                                    sensorData = {
                                        "name": key["friendly_name"],
                                        "protocol": "mqtt",
                                        "modelid": key["model_id"],
                                        "type": sensor_type,
                                        "uniqueid": uniqueid,
                                        "protocol_cfg": {
                                            "friendly_name": key["friendly_name"],
                                            "ieeeAddr": key["ieee_address"],
                                            "model": key["definition"]["model"]
                                        },
                                        "id_v1": new_sensor_id
                                    }
                                    bridgeConfig["sensors"][new_sensor_id] = Sensor.Sensor(sensorData)
                            elif key["model_id"] in motionSensors:
                                logging.info("MQTT: add new motion sensor " + key["model_id"])
                                addHueMotionSensor(key["friendly_name"], "mqtt", {"modelid": key["model_id"], "lightSensor": "on", "friendly_name": key["friendly_name"]})
                            else:
                                logging.info("MQTT: unsupported sensor " + key["model_id"])
            elif msg.topic == "zigbee2mqtt/bridge/log":
                light = getObject(data["meta"]["friendly_name"])
                if data["type"] == "device_announced":
                    if light.config["startup"]["mode"] == "powerfail":
                        logging.info("set last state for " + light.name)
                        payload = {"state": "ON" if light.state["on"] else "OFF"}
                        client.publish(light.protocol_cfg['command_topic'], json.dumps(payload))
                elif data["type"] == "zigbee_publish_error":
                    logging.info(light.name + " is unreachable")
                    light.state["reachable"] = False
            else:
                device_friendlyname = msg.topic[msg.topic.index("/") + 1:]
                device = getObject(device_friendlyname)
                if device:
                    if device.getObjectPath()["resource"] == "sensors":
                        if "battery" in data and isinstance(data["battery"], int):
                            device.config["battery"] = data["battery"]
                        if not device.config["on"]:
                            return
                        convertedPayload = {"lastupdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")}
                        if ("action" in data and data["action"] == "") or ("click" in data and data["click"] == ""):
                            return
                        if device.modelid in motionSensors:
                            convertedPayload["presence"] = data["occupancy"]
                            lightPayload = {"lastupdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")}
                            lightSensor = findLightSensor(device)
                            if "temperature" in data:
                                tempSensor = findTempSensor(device)
                                tempSensor.state = {"temperature": int(data["temperature"] * 100), "lastupdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")}
                            if "illuminance_lux" in data:
                                hue_lightlevel = int(10000 * math.log10(data["illuminance_lux"])) if data["illuminance_lux"] != 0 else 0
                                lightPayload["dark"] = hue_lightlevel <= lightSensor.config["tholddark"]
                                lightPayload["lightlevel"] = hue_lightlevel
                            elif lightSensor.protocol_cfg["lightSensor"] == "on":
                                lightPayload["dark"] = not bridgeConfig["sensors"]["1"].state["daylight"]
                                lightPayload["lightlevel"] = 6000 if lightPayload["dark"] else 25000
                            else:
                                lightPayload["dark"] = True
                                lightPayload["lightlevel"] = 6000
                            lightPayload["daylight"] = not lightPayload["dark"]
                            if lightPayload["dark"] != lightSensor.state["dark"]:
                                lightSensor.dxState["dark"] = current_time
                            lightSensor.state.update(lightPayload)
                            if data["occupancy"] and bridgeConfig["config"]["alarm"]["enabled"] and bridgeConfig["config"]["alarm"]["lasttriggered"] + 300 < current_time.timestamp():
                                logging.info("Alarm triggered, sending email...")
                                requests.post("https://diyhue.org/cdn/mailNotify.php", json={"to": bridgeConfig["config"]["alarm"]["email"], "sensor": device.name}, timeout=10)
                                bridgeConfig["config"]["alarm"]["lasttriggered"] = int(current_time.timestamp())
                        elif device.modelid in standardSensors:
                            convertedPayload.update(standardSensors[device.modelid]["dataConversion"][data[standardSensors[device.modelid]["dataConversion"]["rootKey"]]])
                        for key in convertedPayload.keys():
                            if device.state[key] != convertedPayload[key]:
                                device.dxState[key] = current_time
                        device.state.update(convertedPayload)
                        logging.debug(convertedPayload)
                        if "buttonevent" in convertedPayload and convertedPayload["buttonevent"] in [1001, 2001, 3001, 4001, 5001]:
                            Thread(target=longPressButton, args=[device, convertedPayload["buttonevent"]]).start()
                        rulesProcessor(device, current_time)
                        checkBehaviorInstances(device)
                    elif device.getObjectPath()["resource"] == "lights":
                        state = {"reachable": True}
                        v2State = {}
                        if "state" in data:
                            state["on"] = data["state"] == "ON"
                            v2State.update({"on": {"on": state["on"]}})
                            device.genStreamEvent(v2State)
                        if "brightness" in data:
                            state["bri"] = data["brightness"]
                            v2State.update({"dimming": {"brightness": round(state["bri"] / 2.54, 2)}})
                            device.genStreamEvent(v2State)
                        device.state.update(state)
                        streamGroupEvent(device, v2State)

                on_state_update(msg)
        except Exception as e:
            logging.info("MQTT Exception | " + str(e))

def findLightSensor(sensor: Sensor) -> Optional[Sensor.Sensor]:
    """Finds the light sensor associated with a given sensor."""
    lightSensorUID = sensor.uniqueid[:-1] + "0"
    for key, obj in bridgeConfig["sensors"].items():
        if obj.uniqueid == lightSensorUID:
            return obj
    return None

def findTempSensor(sensor: Sensor) -> Optional[Sensor.Sensor]:
    """Finds the temperature sensor associated with a given sensor."""
    lightSensorUID = sensor.uniqueid[:-1] + "2"
    for key, obj in bridgeConfig["sensors"].items():
        if obj.uniqueid == lightSensorUID:
            return obj
    return None

def convertHexToMac(hexValue: str) -> str:
    """Converts a hexadecimal value to a MAC address."""
    s = '{0:016x}'.format(int(hexValue, 16))
    s = ':'.join(s[i:i + 2] for i in range(0, 16, 2))
    return s

def on_connect(client: mqtt.Client, userdata: Any, flags: Dict[str, int], rc: int) -> None:
    """Handles the MQTT connection event."""
    logging.debug("Connected with result code " + str(rc))
    autodiscoveryTopic = discoveryPrefix + "/light/+/light/config"
    client.subscribe(autodiscoveryTopic)
    client.subscribe("zigbee2mqtt/+")
    client.subscribe("zigbee2mqtt/bridge/devices")
    client.subscribe("zigbee2mqtt/bridge/log")

def mqttServer() -> None:
    """Starts the MQTT server."""
    logging.info("Starting MQTT service...")
    if bridgeConfig["config"]["mqtt"]["mqttUser"] and bridgeConfig["config"]["mqtt"]["mqttPassword"]:
        client.username_pw_set(bridgeConfig["config"]["mqtt"]["mqttUser"], bridgeConfig["config"]["mqtt"]["mqttPassword"])

    if bridgeConfig["config"]["mqtt"]['discoveryPrefix']:
        global discoveryPrefix
        discoveryPrefix = bridgeConfig["config"]["mqtt"]['discoveryPrefix']

    bridgeConfig["config"]["mqtt"].setdefault('mqttCaCerts', None)
    bridgeConfig["config"]["mqtt"].setdefault('mqttCertfile', None)
    bridgeConfig["config"]["mqtt"].setdefault('mqttKeyfile', None)
    bridgeConfig["config"]["mqtt"].setdefault('mqttTls', False)
    bridgeConfig["config"]["mqtt"].setdefault('mqttTlsInsecure', False)

    if bridgeConfig["config"]["mqtt"]["mqttTls"]:
        mqttTlsVersion = ssl.PROTOCOL_TLS
        client.tls_set(
            ca_certs=bridgeConfig["config"]["mqtt"]["mqttCaCerts"],
            certfile=bridgeConfig["config"]["mqtt"]["mqttCertfile"],
            keyfile=bridgeConfig["config"]["mqtt"]["mqttKeyfile"],
            tls_version=mqttTlsVersion
        )
        if bridgeConfig["config"]["mqtt"]["mqttTlsInsecure"]:
            client.tls_insecure_set(bridgeConfig["config"]["mqtt"]["mqttTlsInsecure"])

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(bridgeConfig["config"]["mqtt"]["mqttServer"], bridgeConfig["config"]["mqtt"]["mqttPort"])
    client.loop_forever()
