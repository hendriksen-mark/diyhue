import socket
import logManager
from typing import Optional

logging = logManager.logger.get_logger(__name__)

def getIpAddress() -> Optional[str]:
    """
    Get the local IP address by connecting to an external server.

    Returns:
        Optional[str]: The local IP address or None if an error occurs.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except socket.error as e:
        logging.error(f"Socket error: {e}")
        return None