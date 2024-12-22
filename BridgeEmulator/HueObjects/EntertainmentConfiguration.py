import uuid
import logManager
import weakref
from datetime import datetime, timezone
from HueObjects import genV2Uuid, v1StateToV2, v2StateToV1, setGroupAction, StreamEvent
from typing import Dict, Any, List, Optional, Union

logging = logManager.logger.get_logger(__name__)

class EntertainmentConfiguration:
    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get("name", f"Group {data['id_v1']}")
        self.id_v1: str = data["id_v1"]
        self.id_v2: str = data.get("id_v2", genV2Uuid())
        self.configuration_type: str = data.get("configuration_type", "screen")
        self.lights: List[weakref.ref] = []
        self.action: Dict[str, Union[bool, int, float, str, List[float]]] = {
            "on": False, "bri": 100, "hue": 0, "sat": 254, "effect": "none", "xy": [0.0, 0.0], "ct": 153, "alert": "none", "colormode": "xy"
        }
        self.sensors: List[weakref.ref] = []
        self.type: str = data.get("type", "Entertainment")
        self.locations: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
        self.stream: Dict[str, Union[str, bool, None]] = {"proxymode": "auto", "proxynode": "/bridge", "active": False, "owner": None}
        self.state: Dict[str, bool] = {"all_on": False, "any_on": False}
        self.dxState: Dict[str, Optional[bool]] = {"all_on": None, "any_on": None}

        self._send_stream_event(self.getV2Api(), "add")

    def __del__(self):
        self._send_stream_event({"id": self.id_v2, "type": "grouped_light"}, "delete")
        self._send_stream_event({"id": self.getV2Api()["id"], "type": "entertainment_configuration"}, "delete")
        logging.info(f"{self.name} entertainment area was destroyed.")

    def add_light(self, light: Any) -> None:
        self.lights.append(weakref.ref(light))
        self.locations[light] = [{"x": 0, "y": 0, "z": 0}]

    def update_attr(self, newdata: Dict[str, Any]) -> None:
        newdata.pop("lights", None)
        newdata.pop("locations", None)
        for key, value in newdata.items():
            updateAttribute = getattr(self, key)
            if isinstance(updateAttribute, dict):
                updateAttribute.update(value)
            else:
                setattr(self, key, value)
        self._send_stream_event(self.getV2Api(), "update")

    def update_state(self) -> Dict[str, bool]:
        all_on = bool(self.lights)
        any_on = False
        for light in self.lights:
            if light() and light().state["on"]:
                any_on = True
            else:
                all_on = False
        return {"all_on": all_on, "any_on": any_on}

    def getV2GroupedLight(self) -> Dict[str, Any]:
        return {
            "alert": {"action_values": ["breathe"]},
            "id": self.id_v2,
            "id_v1": f"/groups/{self.id_v1}",
            "on": {"on": self.update_state()["any_on"]},
            "type": "grouped_light"
        }

    def getV1Api(self) -> Dict[str, Any]:
        lights = [light().id_v1 for light in self.lights if light()]
        sensors = [sensor().id_v1 for sensor in self.sensors if sensor()]
        locations = {light.id_v1: [loc[0]["x"], loc[0]["y"], loc[0]["z"]] for light, loc in list(self.locations.items()) if light.id_v1 in lights}
        class_type = "Free" if self.configuration_type == "3dspace" else "TV"
        return {
            "name": self.name,
            "lights": lights,
            "sensors": sensors,
            "type": self.type,
            "state": self.update_state(),
            "recycle": False,
            "class": class_type,
            "action": self.action,
            "locations": locations,
            "stream": self.stream
        }

    def getV2Api(self) -> Dict[str, Any]:
        gradienStripPositions = [
            {"x": -0.4, "y": 0.8, "z": -0.4}, {"x": -0.4, "y": 0.8, "z": 0.0}, {"x": -0.4, "y": 0.8, "z": 0.4},
            {"x": 0.0, "y": 0.8, "z": 0.4}, {"x": 0.4, "y": 0.8, "z": 0.4}, {"x": 0.4, "y": 0.8, "z": 0.0},
            {"x": 0.4, "y": 0.8, "z": -0.4}
        ]
        result = {
            "configuration_type": self.configuration_type,
            "locations": {"service_locations": []},
            "metadata": {"name": self.name},
            "id_v1": f"/groups/{self.id_v1}",
            "stream_proxy": {
                "mode": "auto",
                "node": {
                    "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, self.lights[0]().id_v2 + 'entertainment')) if self.lights else None,
                    "rtype": "entertainment"
                }
            },
            "light_services": [],
            "channels": [],
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, self.id_v2 + 'entertainment_configuration')),
            "type": "entertainment_configuration",
            "name": self.name,
            "status": "active" if self.stream["active"] else "inactive"
        }
        if self.stream["active"]:
            result["active_streamer"] = {"rid": self.stream["owner"], "rtype": "auth_v1"}
        channel_id = 0
        for light in self.lights:
            if light():
                result["light_services"].append({"rtype": "light", "rid": light().id_v2})
                entertainmentUuid = str(uuid.uuid5(uuid.NAMESPACE_URL, light().id_v2 + 'entertainment'))
                result["locations"]["service_locations"].append({
                    "equalization_factor": 1,
                    "positions": self.locations[light()],
                    "service": {"rid": entertainmentUuid, "rtype": "entertainment"},
                    "position": self.locations[light()][0]
                })
                loops = len(gradienStripPositions) if light().modelid in ["LCX001", "LCX002", "LCX003"] else len(self.locations[light()])
                for x in range(loops):
                    channel = {
                        "channel_id": channel_id,
                        "members": [{"index": x, "service": {"rid": entertainmentUuid, "rtype": "entertainment"}}]
                    }
                    if light().modelid in ["LCX001", "LCX002", "LCX003"]:
                        channel["position"] = gradienStripPositions[x]
                    elif light().modelid in ["915005987201", "LCX004", "LCX006"]:
                        if x == 0:
                            channel["position"] = self.locations[light()][0]
                        elif x == 2:
                            channel["position"] = self.locations[light()][1]
                        else:
                            channel["position"] = {
                                "x": (self.locations[light()][0]["x"] + self.locations[light()][1]["x"]) / 2,
                                "y": (self.locations[light()][0]["y"] + self.locations[light()][1]["y"]) / 2,
                                "z": (self.locations[light()][0]["z"] + self.locations[light()][1]["z"]) / 2
                            }
                    else:
                        channel["position"] = self.locations[light()][0]
                    result["channels"].append(channel)
                    channel_id += 1
        return result

    def setV2Action(self, state: Dict[str, Any]) -> None:
        v1State = v2StateToV1(state)
        setGroupAction(self, v1State)
        self.genStreamEvent(state)

    def setV1Action(self, state: Dict[str, Any], scene: Optional[str] = None) -> None:
        setGroupAction(self, state, scene)
        v2State = v1StateToV2(state)
        self.genStreamEvent(v2State)

    def genStreamEvent(self, v2State: Dict[str, Any]) -> None:
        streamMessage = {"data": [{"id": self.id_v2, "type": "grouped_light"}]}
        streamMessage["data"][0].update(v2State)
        self._send_stream_event(streamMessage["data"][0], "update")

    def _send_stream_event(self, data: Dict[str, Any], event_type: str) -> None:
        streamMessage = {
            "creationtime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": [data],
            "id": str(uuid.uuid4()),
            "type": event_type,
            "id_v1": f"/groups/{self.id_v1}"
        }
        StreamEvent(streamMessage)

    def getObjectPath(self) -> Dict[str, str]:
        return {"resource": "groups", "id": self.id_v1}

    def save(self) -> Dict[str, Any]:
        result = {
            "id_v2": self.id_v2,
            "name": self.name,
            "configuration_type": self.configuration_type,
            "lights": [light().id_v1 for light in self.lights if light()],
            "action": self.action,
            "type": self.type,
            "locations": {light.id_v1: loc for light, loc in self.locations.items() if light.id_v1 in [light().id_v1 for light in self.lights if light()]}
        }
        return result
