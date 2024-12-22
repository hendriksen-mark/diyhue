import logManager
import configManager
from lights.protocols import protocols
from time import sleep
from datetime import datetime, timedelta, timezone
from typing import Any

logging = logManager.logger.get_logger(__name__)
bridgeConfig = configManager.bridgeConfig.yaml_config

def syncWithLights(off_if_unreachable: bool) -> None:  # update Hue Bridge lights states
    while True:
        logging.info("start lights sync")
        for key, light in bridgeConfig["lights"].items():
            protocol_name = light.protocol
            if protocol_name in ["mqtt", "flex", "mi_box", "dummy"]:
                continue
            for protocol in protocols:
                if "lights.protocols." + protocol_name == protocol.__name__:
                    try:
                        logging.debug("fetch " + light.name)
                        newState = protocol.get_light_state(light)
                        logging.debug(newState)
                        light.state.update(newState)
                        light.state["reachable"] = True
                    except Exception as e:
                        light.state["reachable"] = False
                        if off_if_unreachable:
                            light.state["on"] = False
                        logging.warning(f"{light.name} is unreachable: {e}")
                    break

        sleep(10)  # wait at least 10 seconds before next sync
        i = 0
        while i < 300:  # sync with lights every 300 seconds or instant if one user is connected
            for key, user in bridgeConfig["apiUsers"].items():
                lu = user.last_use_date
                try:  # in case if last use is not a proper datetime
                    lu = datetime.strptime(lu, "%Y-%m-%dT%H:%M:%S")
                    if abs(datetime.now(timezone.utc).replace(tzinfo=None) - lu) <= timedelta(seconds=2):
                        i = 300
                        break
                except Exception as e:
                    logging.warning(f"{user.last_use_date} is not a proper datetime: {e}")
            i += 1
            sleep(1)
