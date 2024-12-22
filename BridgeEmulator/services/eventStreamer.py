import json
from time import sleep, time

from flask import Response, stream_with_context, Blueprint

import HueObjects
import logManager

logging = logManager.logger.get_logger(__name__)
stream = Blueprint('stream', __name__)

def messageBroker() -> None:
    """
    Continuously checks for events in the HueObjects event stream and logs them.
    Clears the event stream after processing.
    """
    while True:
        if len(HueObjects.eventstream) > 0:
            for event in HueObjects.eventstream:
                logging.debug(event)
            sleep(0.3)  # ensure all devices connected receive the events
            HueObjects.eventstream = []
        sleep(0.2)

@stream.route('/eventstream/clip/v2')
def streamV2Events() -> Response:
    """
    Streams events from the HueObjects event stream to the client.

    Returns:
        Response: A Flask Response object with the event stream.
    """
    def generate():
        """
        Generator function that yields events from the HueObjects event stream.

        Yields:
            str: Formatted event data.
        """
        yield f": hi\n\n"
        while True:
            try:
                if len(HueObjects.eventstream) > 0:
                    for index, messages in enumerate(HueObjects.eventstream):
                        yield f"id: {int(time()) }:{index}\ndata: {json.dumps([messages], separators=(',', ':'))}\n\n"
                    HueObjects.eventstream = []
                sleep(0.2)
            except GeneratorExit:
                logging.info("Client closed the connection.")
                break
            except Exception as e:
                logging.error(f"Error in event stream: {e}")
                break

    return Response(stream_with_context(generate()), mimetype='text/event-stream; charset=utf-8')
