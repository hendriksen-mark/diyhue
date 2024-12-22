import os
import socket
import logManager
from typing import Optional, List

logging = logManager.logger.get_logger(__name__)

if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname: str) -> str:
        """
        Get the IP address of a given network interface.

        Args:
            ifname (str): The name of the network interface.

        Returns:
            str: The IP address of the network interface.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                    bytes(ifname[:15], 'utf-8')))[20:24])

def getIpAddress() -> Optional[str]:
    """
    Get the IP address of the current machine.

    Returns:
        Optional[str]: The IP address of the current machine, or None if it cannot be determined.
    """
    ip: Optional[str] = None

    try:
        ip = socket.gethostbyname(socket.gethostname())
        logging.debug(f"Hostname IP: {ip}")
    except socket.error as e:
        logging.error(f"Error getting hostname IP: {e}")
    
    if (not ip or ip.startswith("127.")) and os.name != "nt":
        interfaces: List[str] = [
            "br0", "br-lan", "eth0", "eth1", "eth2",
            "wlan0", "wlan1", "wifi0", "ath0", "ath1", "ppp0"
        ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                if ip:
                    logging.debug(f"Interface {ifname} IP: {ip}")
                    break
            except IOError as e:
                logging.error(f"Error getting IP for interface {ifname}: {e}")
                continue
    return ip
