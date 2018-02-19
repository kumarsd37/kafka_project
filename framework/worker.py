import logging
from threading import Thread, Event

from framework.clients_initializations import client_initialize_mappings

logger = logging.getLogger(__name__)


class Worker(Thread):

    def __init__(self, message_processor, inbound_client_settings, outbound_client_settings):
        Thread.__init__(self)
        self.message_processor = message_processor
        self.inbound_client_settings = inbound_client_settings
        self.outbound_client_settings = outbound_client_settings
        self.inbound_client = None
        self.outbound_client = None
        self.event = Event()

    def process_and_dispatch(self, message):
        """
        process the message using processor and dispatch the processed result to outbound client.
        :param message: message to be processed
        :type message:
        :return:
        :rtype:
        """
        try:
            logger.debug('raw record {}'.format(message))
            result = self.message_processor(message)
            logger.debug('result by message processor {}'.format(result))
            self.outbound_client.send(result)
            self.inbound_client.post_consume(message)
        except Exception as exc:
            logger.error(exc, exc_info=True)
        finally:
            pass

    def run(self):
        try:
            inbound_client_name = self.inbound_client_settings['name']
            outbound_client_name = self.outbound_client_settings['name']
            logger.debug(client_initialize_mappings)
            inbound_initialize_client = client_initialize_mappings[inbound_client_name]
            outbound_initialize_client = client_initialize_mappings.get(outbound_client_name)
            self.inbound_client = inbound_initialize_client(**self.inbound_client_settings.get('config'))
            self.outbound_client = outbound_initialize_client(**self.outbound_client_settings.get('config'))
            self.event.set()
        except KeyError as exc:
            logger.error(exc, exc_info=True)
            raise exc
        except Exception as exc:
            logger.error(exc, exc_info=True)
            raise exc
        try:
            self.loop()
        finally:
            self.close()

    def clear_event(self):
        if self.event.is_set():
            self.event.clear()

    def loop(self):

        while True:
            messages = self.inbound_client.consume()
            if messages is not None:
                # for each message in batch we are processing the further process.
                for message in messages:
                        self.process_and_dispatch(message)
            if not self.event.is_set():
                break

    def close(self):
        self.inbound_client.close()
        self.outbound_client.close()

# todo: need to work with post_send()
# this need to be configurable from worker settings.



