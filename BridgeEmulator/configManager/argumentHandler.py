import argparse
import logManager
from os import getenv, path
from functions.network import getIpAddress
from subprocess import run, CompletedProcess
from collections import defaultdict
from typing import Dict, Tuple, Optional, Union

logging = logManager.logger.get_logger(__name__)

DEPRECATED_WARNINGS = {
    "scan_on_host_ip": "scan_on_host_ip is Deprecated in commandline and not active, please setup via webui",
    "ip_range": "IP range is Deprecated in commandline and not active, please setup via webui",
    "deconz": "DECONZ is Deprecated in commandline and not active, please setup via webui",
    "disable_online_discover": "disableonlinediscover is Deprecated in commandline and not active, please setup via webui"
}

def get_environment_variable(var: str, boolean: bool = False) -> Union[str, bool, None]:
    """
    Get the value of an environment variable.

    Args:
        var (str): The name of the environment variable.
        boolean (bool): Whether to interpret the value as a boolean.
    """
    value = getenv(var)
    if value is None:
        return False if boolean else None
    if boolean:
        return value.lower() == "true"
    return value

def generate_certificate(mac: str, path: str) -> None:
    """
    Generate a certificate using the provided MAC address and path.

    Args:
        mac (str): The MAC address.
        path (str): The path to save the certificate.
    """
    logging.info("Generating certificate")
    serial = (mac[:6] + "fffe" + mac[-6:]).encode('utf-8')
    result: CompletedProcess = run(["/bin/bash", "/opt/hue-emulator/genCert.sh", serial, path], check=True)
    if result.returncode == 0:
        logging.info("Certificate created")
    else:
        logging.error("Certificate creation failed")

def process_arguments(configDir: str, args: Dict[str, Union[str, bool]]) -> None:
    """
    Process command-line arguments and configure logging and certificates.

    Args:
        configDir (str): The configuration directory.
        args (dict): The command-line arguments.
    """
    configure_logging(args["DEBUG"])
    if not path.isfile(path.join(configDir, "cert.pem")):
        generate_certificate(args["MAC"], configDir)

def parse_arguments() -> Dict[str, Union[str, bool]]:
    """
    Parse command-line arguments and environment variables.

    Returns:
        dict: The dictionary of parsed arguments.
    """
    argumentDict = initialize_argument_dict()

    ap = argparse.ArgumentParser()
    add_arguments(ap)
    args = ap.parse_args()

    set_arguments_from_args_and_env(argumentDict, args)

    log_deprecated_warnings(args)

    logging.info(f"Using Host {argumentDict['HOST_IP']}:{argumentDict['HTTP_PORT']}")
    logging.info(f"Using Host {argumentDict['HOST_IP']}:{argumentDict['HTTPS_PORT']}")

    mac, dockerMAC = get_mac_address(args, argumentDict)

    argumentDict["FULLMAC"] = dockerMAC
    argumentDict["MAC"] = mac

    validate_mac_address(mac)

    if argumentDict['noServeHttps']:
        logging.info("HTTPS Port Disabled")

    return argumentDict

def configure_logging(debug: bool) -> None:
    """
    Configure logging based on the debug flag.

    Args:
        debug (bool): Whether to enable debug logging.
    """
    if debug:
        logging.info("Debug logging enabled!")
    else:
        logManager.logger.configure_logger("INFO")
        logging.info("Debug logging disabled!")

def set_argument(argumentDict: Dict[str, Union[str, bool]], key: str, arg_value: Optional[Union[str, bool]], env_var: str, default: Optional[Union[str, bool]] = None, boolean: bool = False) -> None:
    """
    Set an argument value in the argument dictionary.

    Args:
        argumentDict (dict): The dictionary to store arguments.
        key (str): The key for the argument.
        arg_value: The value from the command-line argument.
        env_var (str): The environment variable name.
        default: The default value if neither arg_value nor env_var is set.
        boolean (bool): Whether to interpret the value as a boolean.
    """
    value = arg_value if arg_value else get_environment_variable(env_var, boolean)
    argumentDict[key] = value if value else default

def initialize_argument_dict() -> Dict[str, Union[str, bool]]:
    """
    Initialize the argument dictionary with default values.

    Returns:
        dict: The initialized argument dictionary.
    """
    argumentDict = defaultdict(lambda: '')
    argumentDict.update({"DEBUG": False, "DOCKER": False, "noLinkButton": False, "noServeHttps": False})
    return argumentDict

def add_arguments(ap: argparse.ArgumentParser) -> None:
    """
    Add command-line arguments to the argument parser.

    Args:
        ap (argparse.ArgumentParser): The argument parser.
    """
    ap.add_argument("--debug", action='store_true', help="Enables debug output")
    ap.add_argument("--bind-ip", help="The IP address to listen on", type=str, default='0.0.0.0')
    ap.add_argument("--config_path", help="Set certificate and config files location", type=str, default='/opt/hue-emulator/config')
    ap.add_argument("--docker", action='store_true', help="Enables setup for use in docker container")
    ap.add_argument("--ip", help="The IP address of the host system (Docker)", type=str)
    ap.add_argument("--http-port", help="The port to listen on for HTTP (Docker)", type=int, default=80)
    ap.add_argument("--https-port", help="The port to listen on for HTTPS (Docker)", type=int, default=443)
    ap.add_argument("--mac", help="The MAC address of the host system (Docker)", type=str)
    ap.add_argument("--no-serve-https", action='store_true', help="Don't listen on port 443 with SSL")
    ap.add_argument("--ip-range", help="Deprecated use webui, Set IP range for light discovery. Format: <START_IP>,<STOP_IP>", type=str)
    ap.add_argument("--sub-ip-range", help="Deprecated use webui, Set SUB IP range for light discovery. Format: <START_IP>,<STOP_IP>", type=str)
    ap.add_argument("--scan-on-host-ip", action='store_true', help="Deprecated use webui, Scan the local IP address when discovering new lights")
    ap.add_argument("--deconz", help="Deprecated use webui, Provide the IP address of your Deconz host. 127.0.0.1 by default.", type=str)
    ap.add_argument("--no-link-button", action='store_true', help="DANGEROUS! Don't require the link button to be pressed to pair the Hue app, just allow any app to connect")
    ap.add_argument("--disable-online-discover", help="Deprecated use webui, Disable Online and Remote API functions")
    ap.add_argument("--TZ", help="Deprecated use webui, Set time zone", type=str)

def set_arguments_from_args_and_env(argumentDict: Dict[str, Union[str, bool]], args: argparse.Namespace) -> None:
    """
    Set arguments from command-line arguments and environment variables.

    Args:
        argumentDict (dict): The dictionary to store arguments.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    set_argument(argumentDict, "DEBUG", args.debug, 'DEBUG', False, True)
    set_argument(argumentDict, "CONFIG_PATH", args.config_path, 'CONFIG_PATH')
    set_argument(argumentDict, "BIND_IP", args.bind_ip, 'BIND_IP')
    set_argument(argumentDict, "HOST_IP", args.ip, 'IP', getIpAddress() if argumentDict["BIND_IP"] == '0.0.0.0' else argumentDict["BIND_IP"])
    set_argument(argumentDict, "HTTP_PORT", args.http_port, 'HTTP_PORT')
    set_argument(argumentDict, "HTTPS_PORT", args.https_port, 'HTTPS_PORT')
    set_argument(argumentDict, "noLinkButton", args.no_link_button, 'noLinkButton', False, True)
    set_argument(argumentDict, "noServeHttps", args.no_serve_https, 'noServeHttps', False, True)
    set_argument(argumentDict, "DOCKER", args.docker, 'DOCKER', False, True)

def log_deprecated_warnings(args: argparse.Namespace) -> None:
    """
    Log warnings for deprecated command-line arguments.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    """
    for arg, warning in DEPRECATED_WARNINGS.items():
        if getattr(args, arg) or get_environment_variable(arg.upper()):
            logging.warning(warning)

def get_mac_address(args: argparse.Namespace, argumentDict: Dict[str, Union[str, bool]]) -> Tuple[str, str]:
    """
    Retrieve the MAC address based on command-line arguments or environment variables.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
        argumentDict (dict): The dictionary of parsed arguments.

    Returns:
        tuple: The MAC address and Docker MAC address.
    """
    mac = retrieve_mac_from_args_or_env(args, 'mac')
    if mac:
        dockerMAC = mac
    else:
        dockerMAC, mac = retrieve_mac_from_system(argumentDict["HOST_IP"])
    return mac.replace(":", ""), dockerMAC

def retrieve_mac_from_args_or_env(args: argparse.Namespace, var: str) -> Optional[str]:
    """
    Retrieve the MAC address from command-line arguments or environment variables.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
        var (str): The variable name.

    Returns:
        str: The MAC address.
    """
    mac = getattr(args, var)
    if mac and mac.replace(":", "").capitalize() != "XXXXXXXXXXXX":
        return mac
    mac = get_environment_variable(var.upper())
    if mac and mac.strip('\u200e').replace(":", "").capitalize() != "XXXXXXXXXXXX":
        return mac.strip('\u200e')
    return None

def retrieve_mac_from_system(host_ip: str) -> Tuple[str, str]:
    """
    Retrieve the MAC address from the system.

    Args:
        host_ip (str): The host IP address.

    Returns:
        tuple: The Docker MAC address and MAC address.
    """
    result: CompletedProcess = run("cat /sys/class/net/$(ip -o addr | grep %s | awk '{print $2}')/address" % host_ip, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        dockerMAC = result.stdout.strip()
        mac = dockerMAC.replace(":", "")
        return dockerMAC, mac
    else:
        logging.error("Failed to retrieve MAC address")
        raise SystemExit("CRITICAL! Failed to retrieve MAC address")

def validate_mac_address(mac: str) -> None:
    """
    Validate the provided MAC address.

    Args:
        mac (str): The MAC address to validate.
    """
    if mac.capitalize() == "XXXXXXXXXXXX" or mac == "":
        logging.error(f"No valid MAC address provided {mac}")
        logging.error("To fix this visit: https://diyhue.readthedocs.io/en/latest/getting_started.html")
        raise SystemExit(f"CRITICAL! No valid MAC address provided {mac}")
    else:
        logging.info(f"Host MAC given as {mac}")
