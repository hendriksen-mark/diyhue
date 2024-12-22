import logManager
from datetime import datetime, timezone
from typing import List, Dict, Any

logging = logManager.logger.get_logger(__name__)

class Rule:
    def __init__(self, data: Dict[str, Any]):
        self.name: str = data["name"]
        self.id_v1: str = data["id_v1"]
        self.actions: List[Dict[str, Any]] = data["actions"] if "actions" in data else []
        self.conditions: List[Dict[str, Any]] = data["conditions"] if "conditions" in data else []
        self.owner: str = data["owner"]
        self.status: str = data["status"] if "status" in data else "enabled"
        self.recycle: bool = data["recycle"] if "recycle" in data else False
        self.created: str = data["created"] if "created" in data else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        self.lasttriggered: str = data["lasttriggered"] if "lasttriggered" in data else "none"
        self.timestriggered: int = data["timestriggered"] if "timestriggered" in data else 0

    def __del__(self):
        logging.info(f"Rule '{self.name}' was destroyed.")

    def add_actions(self, action: Dict[str, Any]) -> None:
        self.actions.append(action)

    def add_conditions(self, condition: Dict[str, Any]) -> None:
        self.conditions.append(condition)

    def getObjectPath(self) -> Dict[str, str]:
        return {"resource": "rules", "id": self.id_v1}

    def getV1Api(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "owner": self.owner.username,
            "created": self.created,
            "lasttriggered": self.lasttriggered,
            "timestriggered": self.timestriggered,
            "status": self.status,
            "recycle": self.recycle,
            "conditions": self.conditions,
            "actions": self.actions
        }
        return result

    def update_attr(self, newdata: Dict[str, Any]) -> None:
        for key, value in newdata.items():
            updateAttribute = getattr(self, key)
            if isinstance(updateAttribute, dict):
                updateAttribute.update(value)
                setattr(self, key, updateAttribute)
            else:
                setattr(self, key, value)

    def save(self) -> Dict[str, Any]:
        return self.getV1Api()
