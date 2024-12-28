from configManager import configInit
from configManager.argumentHandler import parse_arguments, generate_certificate
import os
import pathlib
import subprocess
import logManager
import yaml
import uuid
import weakref
from copy import deepcopy
from HueObjects import Light, Group, EntertainmentConfiguration, Scene, ApiUser, Rule, ResourceLink, Schedule, Sensor, BehaviorInstance, SmartScene
from typing import Any, Dict, Optional, Union

try:
    from time import tzset
except ImportError:
    tzset = None

logging = logManager.logger.get_logger(__name__)

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True

def _open_yaml(path: str) -> Any:
    """
    Open a YAML file and return its contents.

    Args:
        path (str): The path to the YAML file.

    Returns:
        Any: The contents of the YAML file.
    """
    with open(path, 'r', encoding="utf-8") as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)

def _write_yaml(path: str, contents: Any) -> None:
    """
    Write contents to a YAML file.

    Args:
        path (str): The path to the YAML file.
        contents (Any): The contents to write to the YAML file.
    """
    with open(path, 'w', encoding="utf-8") as fp:
        yaml.dump(contents, fp, Dumper=NoAliasDumper, allow_unicode=True, sort_keys=False)

class Config:
    yaml_config: Optional[Dict[str, Any]] = None
    argsDict: Dict[str, Any] = parse_arguments()
    configDir: str = argsDict["CONFIG_PATH"]
    runningDir: str = str(pathlib.Path(__file__)).replace("/configManager/configHandler.py", "")

    def __init__(self) -> None:
        """
        Initialize the Config class.
        """
        if not os.path.exists(self.configDir):
            os.makedirs(self.configDir)

    def _set_default_config_values(self, config: Dict[str, Any]) -> None:
        """
        Set default configuration values.

        Args:
            config (Dict[str, Any]): The configuration dictionary.
        """
        defaults = {
            "Remote API enabled": False,
            "Hue Essentials key": str(uuid.uuid1()).replace('-', ''),
            "discovery": True,
            "IP_RANGE": {
                "IP_RANGE_START": 0,
                "IP_RANGE_END": 255,
                "SUB_IP_RANGE_START": int(self.argsDict["HOST_IP"].split('.')[2]),
                "SUB_IP_RANGE_END": int(self.argsDict["HOST_IP"].split('.')[2])
            },
            "scanonhostip": False,
            "factorynew": True,
            "mqtt":{"enabled":False},
            "deconz":{"enabled":False},
            "alarm":{"enabled": False,"lasttriggered": 0},
            "port":{"enabled": False,"ports": [80]},
            "apiUsers":{},
            "apiversion":"1.67.0",
            "name":"DiyHue Bridge",
            "netmask":"255.255.255.0",
            "swversion":"1967054020",
            "timezone": "Europe/London",
            "linkbutton":{"lastlinkbuttonpushed": 1599398980},
            "users":{"admin@diyhue.org":{"password":"pbkdf2:sha256:150000$bqqXSOkI$199acdaf81c18f6ff2f29296872356f4eb78827784ce4b3f3b6262589c788742"}},
            "hue": {},
            "tradfri": {},
            "homeassistant": {"enabled": False},
            "govee": {"enabled": False, "api_key": ""},
            "yeelight": {"enabled": True},
            "native_multi": {"enabled": True},
            "tasmota": {"enabled": True},
            "wled": {"enabled": True},
            "shelly": {"enabled": True},
            "esphome": {"enabled": True},
            "hyperion": {"enabled": True},
            "tpkasa": {"enabled": True},
            "elgato": {"enabled": True},
            "zigbee_device_discovery_info": {"status": "ready"},
            "swupdate2": {
                "autoinstall": {"on": False, "updatetime": "T14:00:00"},
                "bridge": {"lastinstall": "2020-12-11T17:08:55", "state": "noupdates"},
                "checkforupdate": False,
                "lastchange": "2020-12-13T10:30:15",
                "state": "noupdates",
                "install": False
            }
        }
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
        return config

    def _upgrade_config(self, config: Dict[str, Any]) -> None:
        """
        Upgrade the configuration if necessary.

        Args:
            config (Dict[str, Any]): The configuration dictionary.
        """
        if int(config["swversion"]) < 1958077010:
            config["swversion"] = "1967054020"
        if float(config["apiversion"][:3]) < 1.56:
            config["apiversion"] = "1.67.0"
        if "linkbutton" not in config or type(config["linkbutton"]) == bool or "lastlinkbuttonpushed" not in config["linkbutton"]:
            config["linkbutton"] = {"lastlinkbuttonpushed": 1599398980}
        return config

    def _load_yaml_file(self, filename: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Load a YAML file and return its contents.

        Args:
            filename (str): The name of the YAML file.
            default (Optional[Dict[str, Any]]): The default value if the file does not exist.

        Returns:
            Optional[Dict[str, Any]]: The contents of the YAML file or the default value.
        """
        path = os.path.join(self.configDir, filename)
        if os.path.exists(path):
            return _open_yaml(path)
        return default

    def _load_lights(self) -> None:
        """
        Load lights from the YAML configuration.
        """
        lights = self._load_yaml_file("lights.yaml", {})
        for light, data in lights.items():
            data["id_v1"] = light
            self.yaml_config["lights"][light] = Light.Light(data)

    def _load_groups(self) -> None:
        """
        Load groups from the YAML configuration.
        """
        #create group 0
        self.yaml_config["groups"]["0"] = Group.Group({"name":"Group 0","id_v1": "0","type":"LightGroup","state":{"all_on":False,"any_on":True},"recycle":False,"action":{"on":False,"bri":165,"hue":8418,"sat":140,"effect":"none","xy":[0.6635,0.2825],"ct":366,"alert":"select","colormode":"hs"}})
        for key, light in self.yaml_config["lights"].items():
            self.yaml_config["groups"]["0"].add_light(light)
        # create groups
        groups = self._load_yaml_file("groups.yaml", {})
        for group, data in groups.items():
            data["id_v1"] = group
            if data["type"] == "Entertainment":
                self.yaml_config["groups"][group] = EntertainmentConfiguration.EntertainmentConfiguration(data)
                for light in data["lights"]:
                    self.yaml_config["groups"][group].add_light(self.yaml_config["lights"][light])
                if "locations" in data:
                    for light, location in data["locations"].items():
                        lightObj = self.yaml_config["lights"][light]
                        self.yaml_config["groups"][group].locations[lightObj] = location
            else:
                if "owner" in data and isinstance(data["owner"], dict):
                    data["owner"] = self.yaml_config["apiUsers"][list(self.yaml_config["apiUsers"])[0]]
                elif "owner" not in data:
                    data["owner"] = self.yaml_config["apiUsers"][list(self.yaml_config["apiUsers"])[0]]
                else:
                    data["owner"] = self.yaml_config["apiUsers"][data["owner"]]
                self.yaml_config["groups"][group] = Group.Group(data)
                for light in data["lights"]:
                    self.yaml_config["groups"][group].add_light(self.yaml_config["lights"][light])

    def _load_scenes(self) -> None:
        """
        Load scenes from the YAML configuration.
        """
        scenes = self._load_yaml_file("scenes.yaml", {})
        for scene, data in scenes.items():
            data["id_v1"] = scene
            if data["type"] == "GroupScene":
                group = weakref.ref(self.yaml_config["groups"][data["group"]])
                data["lights"] = group().lights
                data["group"] = group
            else:
                data["lights"] = [weakref.ref(self.yaml_config["lights"][light]) for light in data["lights"]]
            data["owner"] = self.yaml_config["apiUsers"][data["owner"]]
            self.yaml_config["scenes"][scene] = Scene.Scene(data)
            for light, lightstate in data["lightstates"].items():
                lightObj = self.yaml_config["lights"][light]
                self.yaml_config["scenes"][scene].lightstates[lightObj] = lightstate

    def _load_smart_scenes(self) -> None:
        """
        Load smart scenes from the YAML configuration.
        """
        smart_scenes = self._load_yaml_file("smart_scene.yaml", {})
        for scene, data in smart_scenes.items():
            data["id_v1"] = scene
            self.yaml_config["smart_scene"][scene] = SmartScene.SmartScene(data)

    def _load_rules(self) -> None:
        """
        Load rules from the YAML configuration.
        """
        rules = self._load_yaml_file("rules.yaml", {})
        for rule, data in rules.items():
            data["id_v1"] = rule
            data["owner"] = self.yaml_config["apiUsers"][data["owner"]]
            self.yaml_config["rules"][rule] = Rule.Rule(data)

    def _load_schedules(self) -> None:
        """
        Load schedules from the YAML configuration.
        """
        schedules = self._load_yaml_file("schedules.yaml", {})
        for schedule, data in schedules.items():
            data["id_v1"] = schedule
            self.yaml_config["schedules"][schedule] = Schedule.Schedule(data)

    def _load_sensors(self) -> None:
        """
        Load sensors from the YAML configuration.
        """
        sensors = self._load_yaml_file("sensors.yaml", {})
        for sensor, data in sensors.items():
            data["id_v1"] = sensor
            self.yaml_config["sensors"][sensor] = Sensor.Sensor(data)
            self.yaml_config["groups"]["0"].add_sensor(self.yaml_config["sensors"][sensor])
        if not sensors:
            data = {"modelid": "PHDL00", "name": "Daylight", "type": "Daylight", "id_v1": "1"}
            self.yaml_config["sensors"]["1"] = Sensor.Sensor(data)
            self.yaml_config["groups"]["0"].add_sensor(self.yaml_config["sensors"]["1"])

    def _load_resourcelinks(self) -> None:
        """
        Load resource links from the YAML configuration.
        """
        resourcelinks = self._load_yaml_file("resourcelinks.yaml", {})
        for resourcelink, data in resourcelinks.items():
            data["id_v1"] = resourcelink
            data["owner"] = self.yaml_config["apiUsers"][data["owner"]]
            self.yaml_config["resourcelinks"][resourcelink] = ResourceLink.ResourceLink(data)

    def _load_behavior_instances(self) -> None:
        """
        Load behavior instances from the YAML configuration.
        """
        behavior_instances = self._load_yaml_file("behavior_instance.yaml", {})
        for behavior_instance, data in behavior_instances.items():
            self.yaml_config["behavior_instance"][behavior_instance] = BehaviorInstance.BehaviorInstance(data)

    def load_config(self) -> None:
        """
        Load the entire configuration from YAML files.
        """
        self.yaml_config = {
            "apiUsers": {}, "lights": {}, "groups": {}, "scenes": {}, "config": {}, "rules": {}, "resourcelinks": {}, "schedules": {}, "sensors": {}, "behavior_instance": {}, "geofence_clients": {}, "smart_scene": {}, "temp": {"eventstream": [], "scanResult": {"lastscan": "none"}, "detectedLights": [], "gradientStripLights": {}}
        }
        try:
            config = self._load_yaml_file("config.yaml", {})
            if "timezone" not in config:
                logging.warn("No Time Zone in config, please set Time Zone in webui, default to Europe/London")
                config["timezone"] = "Europe/London"
            os.environ['TZ'] = config["timezone"]
            if tzset is not None:
                tzset()
            if "whitelist" in config:
                for user, data in config["whitelist"].items():

                    self.yaml_config["apiUsers"][user] = ApiUser.ApiUser(user, data["name"], data["client_key"], data["create_date"], data["last_use_date"])
                del config["whitelist"]
            config = self._set_default_config_values(config)
            config = self._upgrade_config(config)
            self.yaml_config["config"] = config

            self._load_lights()
            self._load_groups()
            self._load_scenes()
            self._load_smart_scenes()
            self._load_rules()
            self._load_schedules()
            self._load_sensors()
            self._load_resourcelinks()
            self._load_behavior_instances()

            logging.info("Config loaded")
        except Exception:
            logging.exception("CRITICAL! Config file was not loaded")
            raise SystemExit("CRITICAL! Config file was not loaded")
        bridgeConfig = self.yaml_config

    def save_config(self, backup: bool = False, resource: str = "all") -> None:
        """
        Save the current configuration to YAML files.

        Args:
            backup (bool): Whether to save a backup of the configuration.
            resource (str): The specific resource to save or "all" to save everything.
        """
        path = self.configDir + '/'
        if backup:
            path = self.configDir + '/backup/'
            if not os.path.exists(path):
                os.makedirs(path)
        if resource in ["all", "config"]:
            config = self.yaml_config["config"]
            config["whitelist"] = {}
            for user, obj in self.yaml_config["apiUsers"].items():
                config["whitelist"][user] = obj.save()
            _write_yaml(path + "config.yaml", config)
            logging.debug("Dump config file " + path + "config.yaml")
            if resource == "config":
                return
        saveResources = []
        if resource == "all":
            saveResources = ["lights", "groups", "scenes", "rules", "resourcelinks", "schedules", "sensors", "behavior_instance", "smart_scene"]
        else:
            saveResources.append(resource)
        for object in saveResources:
            filePath = path + object + ".yaml"
            dumpDict = {}
            for element in self.yaml_config[object]:
                if element != "0":
                    savedData = self.yaml_config[object][element].save()
                    if savedData:
                        dumpDict[self.yaml_config[object][element].id_v1] = savedData
            _write_yaml(filePath, dumpDict)
            logging.debug("Dump config file " + filePath)

    def reset_config(self) -> None:
        """
        Reset the configuration to default values.
        """
        self.save_config(backup=True)
        try:
            subprocess.run(f'rm -r {self.configDir}/*.yaml', check=True)
        except subprocess.CalledProcessError:
            logging.exception("Something went wrong when deleting the config")
        self.load_config()

    def remove_cert(self) -> None:
        """
        Remove the current certificate and generate a new one.
        """
        try:
            subprocess.run(f'mv {self.configDir}/cert.pem {self.configDir}/backup/', check=True)
            logging.info("Certificate removed")
        except subprocess.CalledProcessError:
            logging.exception("Something went wrong when deleting the certificate")
        generate_certificate(self.argsDict["MAC"], self.argsDict["CONFIG_PATH"])

    def restore_backup(self) -> None:
        """
        Restore the configuration from a backup.
        """
        try:
            subprocess.run(f'rm -r {self.configDir}/*.yaml', check=True)
        except subprocess.CalledProcessError:
            logging.exception("Something went wrong when deleting the config")
        subprocess.run(f'cp -r {self.configDir}/backup/*.yaml {self.configDir}/', shell=True, check=True)
        self.load_config()

    def download_config(self) -> str:
        """
        Download the current configuration as a tar file.

        Returns:
            str: The path to the tar file containing the configuration.
        """
        self.save_config()
        subprocess.run(f'tar --exclude=\'config_debug.yaml\' -cvf {self.configDir}/config.tar ' + self.configDir + '/*.yaml', shell=True, capture_output=True, text=True)
        return f"{self.configDir}/config.tar"

    def download_log(self) -> str:
        """
        Download the log files as a tar file.

        Returns:
            str: The path to the tar file containing the log files.
        """
        subprocess.run(f'tar -cvf {self.configDir}/diyhue_log.tar {self.runningDir}/*.log*', shell=True, check=True)
        return f"{self.configDir}/diyhue_log.tar"

    def download_debug(self) -> str:
        """
        Download the debug information as a tar file.

        Returns:
            str: The path to the tar file containing the debug information.
        """
        debug = deepcopy(self.yaml_config["config"])
        debug["whitelist"] = "privately"
        debug["apiUsers"] = "privately"
        debug["Hue Essentials key"] = "privately"
        debug["users"] = "privately"
        if debug["mqtt"]["enabled"] or "mqttPassword" in debug["mqtt"]:
            debug["mqtt"]["mqttPassword"] = "privately"
        if debug["homeassistant"]["enabled"] or "homeAssistantToken" in debug["homeassistant"]:
            debug["homeassistant"]["homeAssistantToken"] = "privately"
        if debug["hue"]:
            debug["hue"]["hueUser"] = "privately"
            debug["hue"]["hueKey"] = "privately"
        if debug["tradfri"]:
            debug["tradfri"]["psk"] = "privately"
        if debug["alarm"]["enabled"] or "email" in debug["alarm"]:
            debug["alarm"]["email"] = "privately"
        if debug["govee"]["enabled"] or "api_key" in debug["govee"]:
            debug["govee"]["api_key"] = "privately"
        info = {}
        info["OS"] = os.uname().sysname
        info["Architecture"] = os.uname().machine
        info["os_version"] = os.uname().version
        info["os_release"] = os.uname().release
        info["Hue-Emulator Version"] = subprocess.run("stat -c %y HueEmulator3.py", shell=True, capture_output=True, text=True).stdout.replace("\n", "")
        info["WebUI Version"] = subprocess.run("stat -c %y flaskUI/templates/index.html", shell=True, capture_output=True, text=True).stdout.replace("\n", "")
        info["arguments"] = {k: str(v) for k, v in self.argsDict.items()}
        _write_yaml(f"{self.configDir}/config_debug.yaml", debug)
        _write_yaml(f"{self.configDir}/system_info.yaml", info)
        subprocess.run(f'tar --exclude=\'config.yaml\' -cvf {self.configDir}/config_debug.tar {self.configDir}/*.yaml {self.runningDir}/*.log* ', shell=True, capture_output=True, text=True)
        subprocess.run(f'rm -r {self.configDir}/config_debug.yaml', check=True)
        return f"{self.configDir}/config_debug.tar"

    def write_args(self, args: Dict[str, Any]) -> None:
        """
        Write arguments to the configuration.

        Args:
            args (Dict[str, Any]): The arguments to write.
        """
        self.yaml_config = configInit.write_args(args, self.yaml_config)

    def generate_security_key(self) -> None:
        """
        Generate a new security key for the configuration.
        """
        self.yaml_config = configInit.generate_security_key(self.yaml_config)
