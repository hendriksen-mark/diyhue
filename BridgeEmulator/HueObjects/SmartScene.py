import uuid
import logManager
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from HueObjects import genV2Uuid, StreamEvent

logging = logManager.logger.get_logger(__name__)

class SmartScene:
    DEFAULT_SPEED = 60000  # ms

    def __init__(self, data: Dict[str, Any]) -> None:
        self.name: str = data["name"]
        self.id_v1: str = data["id_v1"]
        self.id_v2: str = data.get("id_v2", genV2Uuid())
        self.appdata: Dict[str, Any] = data.get("appdata", {})
        self.type: str = data.get("type", "smart_scene")
        self.image: Optional[str] = data.get("image")
        self.action: str = data.get("action", "deactivate")
        self.lastupdated: str = data.get("lastupdated", self._current_time())
        self.timeslots: Dict[str, Any] = data.get("timeslots", {})
        self.recurrence: Dict[str, Any] = data.get("recurrence", {})
        self.speed: int = data.get("transition_duration", self.DEFAULT_SPEED)
        self.group: Optional[Dict[str, Any]] = data.get("group")
        self.state: str = data.get("state", "inactive")
        self.active_timeslot: int = data.get("active_timeslot", 0)

        self._send_stream_event(self.getV2Api(), "add")

    def __del__(self) -> None:
        self._send_stream_event({"id": self.id_v2, "type": "smart_scene"}, "delete")
        logging.info(f"{self.name} smart_scene was destroyed.")

    def _send_stream_event(self, data: Dict[str, Any], event_type: str) -> None:
        streamMessage = {
            "creationtime": self._current_time(),
            "data": [data],
            "id": str(uuid.uuid4()),
            "type": event_type,
            "id_v1": f"/smart_scene/{self.id_v1}"
        }
        StreamEvent(streamMessage)

    def activate(self, data: Dict[str, Any]) -> None:
        recall_action = data.get("recall", {}).get("action")
        if recall_action == "activate":
            self._activate_scene()
        elif recall_action == "deactivate":
            self._deactivate_scene()

    def _activate_scene(self) -> None:
        logging.debug(f"activate smart_scene: {self.name} scene: {self.active_timeslot}")
        self.state = "active"
        if datetime.now().strftime("%A").lower() in self.recurrence:
            from flaskUI.v2restapi import getObject
            target_object = getObject(self.timeslots[self.active_timeslot]["target"]["rtype"], self.timeslots[self.active_timeslot]["target"]["rid"])
            putDict = {"recall": {"action": "active", "duration": self.speed}}
            target_object.activate(putDict)

    def _deactivate_scene(self) -> None:
        from functions.scripts import findGroup
        group = findGroup(self.group["rid"])
        group.setV1Action(state={"on": False})
        logging.debug(f"deactivate smart_scene: {self.name}")
        self.state = "inactive"

    def getV2Api(self) -> Dict[str, Any]:
        result = {
            "metadata": {
                "name": self.name
            },
            "id": self.id_v2,
            "id_v1": f"/smart_scene/{self.id_v1}",
            "group": self.group,
            "type": "smart_scene",
            "week_timeslots": [{"timeslots": self.timeslots, "recurrence": self.recurrence}],
            "transition_duration": self.speed,
            "state": self.state,
            "active_timeslot": {
                "timeslot_id": self.active_timeslot if self.active_timeslot >= 0 else len(self.timeslots) - 1,
                "weekday": datetime.now().strftime("%A").lower()
            }
        }
        if self.image:
            result["metadata"]["image"] = {"rid": self.image, "rtype": "public_image"}
        return result

    def update_attr(self, newdata: Dict[str, Any]) -> None:
        self.lastupdated = self._current_time()
        for key, value in newdata.items():
            updateAttribute = getattr(self, key)
            if isinstance(updateAttribute, dict):
                updateAttribute.update(value)
                setattr(self, key, updateAttribute)
            else:
                setattr(self, key, value)

    def save(self) -> Dict[str, Any]:
        result = {
            "id_v2": self.id_v2,
            "name": self.name,
            "appdata": self.appdata,
            "type": self.type,
            "image": self.image,
            "lastupdated": self.lastupdated,
            "state": self.state,
            "group": self.group,
            "active_timeslot": self.active_timeslot,
            "speed": self.speed or self.DEFAULT_SPEED
        }
        if self.timeslots:
            result["timeslots"] = self.timeslots
            result["recurrence"] = self.recurrence
        return result

    @staticmethod
    def _current_time() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
