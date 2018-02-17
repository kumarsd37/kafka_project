import json

__author__ = 'pavan.tummalapalli'

import logging

from container import Container

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys
import signal

# signal handler for Ctrl+C key press
def signal_handler(signal, frame):
    logger.info('pressed Ctrl+C!')
    Container.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class MessageProcessor:

    @staticmethod
    def get_and_send(message):
        return message.value


def main():
    json_settings = json.load(open('settings.json'))
    Container.create_container(MessageProcessor.get_and_send, json_settings)
    Container.start()


if __name__ == '__main__':

    main()