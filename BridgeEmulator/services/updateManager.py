import requests
import subprocess
from datetime import datetime, timezone
from typing import List

import configManager
import logManager

bridgeConfig = configManager.bridgeConfig.yaml_config
logging = logManager.logger.get_logger(__name__)

def versionCheck() -> None:
    swversion = bridgeConfig["config"]["swversion"]
    url = f"https://firmware.meethue.com/v1/checkupdate/?deviceTypeId=BSB002&version={swversion}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        device_data = response.json()
        if device_data["updates"]:
            new_version = str(device_data["updates"][-1]["version"])
            new_versionName = str(device_data["updates"][-1]["versionName"][:4] + ".0")
            if new_version > swversion:
                logging.info(f"swversion number update from Philips, old: {swversion} new: {new_version}")
                bridgeConfig["config"]["swversion"] = new_version
                bridgeConfig["config"]["apiversion"] = new_versionName
                update_swupdate2_timestamps()
            else:
                logging.info("swversion higher than Philips")
        else:
            logging.info("no swversion number update from Philips")
    except requests.RequestException as e:
        logging.error(f"No connection to Philips: {e}")

def githubCheck() -> None:
    creation_time = get_file_creation_time("HueEmulator3.py")
    publish_time = get_github_publish_time("https://api.github.com/repos/diyhue/diyhue/branches/master")
    
    logging.debug(f"creation_time diyHue : {creation_time}")
    logging.debug(f"publish_time  diyHue : {publish_time}")

    if publish_time > creation_time:
        logging.info("update on github")
        bridgeConfig["config"]["swupdate2"]["state"] = "allreadytoinstall"
    elif githubUICheck():
        logging.info("UI update on github")
        bridgeConfig["config"]["swupdate2"]["state"] = "anyreadytoinstall"
    else:
        logging.info("no update for diyHue or UI on github")
        bridgeConfig["config"]["swupdate2"]["state"] = "noupdates"
        bridgeConfig["config"]["swupdate2"]["bridge"]["state"] = "noupdates"

    bridgeConfig["config"]["swupdate2"]["checkforupdate"] = False

def githubUICheck() -> bool:
    creation_time = get_file_creation_time("flaskUI/templates/index.html")
    publish_time = get_github_publish_time("https://api.github.com/repos/diyhue/diyHueUI/releases/latest")
    
    logging.debug(f"creation_time UI : {creation_time}")
    logging.debug(f"publish_time  UI : {publish_time}")

    return publish_time > creation_time

def get_file_creation_time(filepath: str) -> str:
    try:
        creation_time = subprocess.run(f"stat -c %y {filepath}", shell=True, capture_output=True, text=True)
        creation_time_arg1 = creation_time.stdout.replace(".", " ").split(" ") if creation_time.stdout else "2999-01-01 01:01:01.000000000 +0100\n".replace(".", " ").split(" ")
        return parse_creation_time(creation_time_arg1)
    except subprocess.SubprocessError as e:
        logging.error(f"Error getting file creation time: {e}")
        return "2999-01-01 01:01:01"

def get_github_publish_time(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        device_data = response.json()
        if "commit" in device_data:
            return datetime.strptime(device_data["commit"]["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H")
        elif "published_at" in device_data:
            return datetime.strptime(device_data["published_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H")
    except requests.RequestException as e:
        logging.error(f"No connection to GitHub: {e}")
        return "1970-01-01 00:00:00"

def parse_creation_time(creation_time_arg1: List[str]) -> str:
    try:
        if len(creation_time_arg1) < 4:
            creation_time = f"{creation_time_arg1[0]} {creation_time_arg1[1]}".replace('\n', '')
            return datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S").astimezone(timezone.utc).strftime("%Y-%m-%d %H")
        else:
            creation_time = f"{creation_time_arg1[0]} {creation_time_arg1[1]} {creation_time_arg1[3]}".replace('\n', '')
            return datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S %z").astimezone(timezone.utc).strftime("%Y-%m-%d %H")
    except ValueError as e:
        logging.error(f"Error parsing creation time: {e}")
        return "2999-01-01 01:01:01"

def update_swupdate2_timestamps() -> None:
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    bridgeConfig["config"]["swupdate2"]["lastchange"] = current_time
    bridgeConfig["config"]["swupdate2"]["bridge"]["lastinstall"] = current_time

def githubInstall() -> None:
    if bridgeConfig["config"]["swupdate2"]["state"] in ["allreadytoinstall", "anyreadytoinstall"]:
        subprocess.Popen(f"sh githubInstall.sh {bridgeConfig['config']['ipaddress']} {bridgeConfig['config']['swupdate2']['state']}", shell=True, close_fds=True)
        bridgeConfig["config"]["swupdate2"]["state"] = "installing"

def startupCheck() -> None:
    if bridgeConfig["config"]["swupdate2"]["install"]:
        bridgeConfig["config"]["swupdate2"]["install"] = False
        update_swupdate2_timestamps()
    versionCheck()
    githubCheck()
