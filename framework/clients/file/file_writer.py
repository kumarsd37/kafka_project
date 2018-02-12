
__author__ = 'pavan.tummalapalli'

import queue
from abstract_client import AbstractProducer
import threading
import logging

logger = logging.getLogger(__name__)


class Event:

    def __init__(self):
        self._set = False

    def set(self):
        self._set = True

    def is_set(self):
        return self._set

    def clear(self):
        self._set = True


class FileWriter(AbstractProducer):
    """ class for writing to a file with concurrent support """

    def __init__(self, file=None, mode='w', encoding=None, max_queue_size=None):
        """
        constructor for creating a file handler
        :param file: file to open
        :type file: str
        :param mode: mode for opening file. default mode is w(write)
        :type mode: str
        :param encoding: encoding is the name of the encoding encode the file.
        :type encoding: str
        :param max_queue_size: max queue size to store the messages in the queue
        :type max_queue_size: int
        :raises IOError
        """
        try:
            self._file_handler = open(file=file, mode=mode, encoding=encoding)
        except IOError as exc:
            raise exc
        self.queue = queue.Queue(maxsize=max_queue_size)

        self.event = Event()
        self.event.set()

        self.start()

    def pre_send(self, *args, **kwargs):
        pass

    def send(self, message, **kwargs):
        """
        send the message to internal queue
        :param message: message that writes to file
        :type message: str
        """
        self.write(message)

    def post_send(self, *args, **kwargs):
        pass

    def serialize_message(self, message, *args, **kwargs):
        pass

    def write(self, message):
        """
        put message to queue
        :param message: message
        :type message: str
        """
        self.queue.put(message)

    def _write_to_file(self):
        message = self.queue.get()
        self.queue.task_done()
        self._file_handler.write(message)
        self._file_handler.flush()


    def _write(self):
        """
        get the message from the queue and writes to file.
        """
        while True:
            self._write_to_file()
            if not self.event.is_set():
                break

    def start(self):
        """
        start writing to the file in separate thread.
        :return:
        :rtype:
        """
        self.thread = threading.Thread(target=self._write)
        self.thread.setDaemon(True)
        self.thread.start()

    def close(self, *args, **kwargs):
        """
        unset the event object and close the file_handler.
        we can specify close_timeout to sleep for some time before closing the file handler.
        """
        if self.event.is_set():
            self.event.clear()

        while not self.queue.empty():
            logger.info('queue size is {}'.format(self.queue.qsize()))
            self._write_to_file()

        logger.info('queue size is {}'.format(self.queue.qsize()))
        self._file_handler.close()



















