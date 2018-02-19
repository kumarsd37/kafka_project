import threading
import time

__author__ = 'pavan.tummalapalli'

import logging
import os
import os.path

from framework.abstract_client import AbstractProducer

logger = logging.getLogger(__name__)


class FileWriter(AbstractProducer):
    """ class for writing to a file with concurrent support """

    def __init__(self, file=None, mode='a', encoding=None):
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
            file_with_thread_id = self.append_thread_id_to_file(file)
            self._file_handler = open(file=file_with_thread_id, mode=mode, encoding=encoding)
        except IOError as exc:
            raise exc

    def pre_send(self, *args, **kwargs):
        pass

    def send(self, message, **kwargs):
        """
        send the message to internal queue
        :param message: message that writes to file
        :type message: str
        """
        self._file_handler.write(message)
        self._file_handler.flush()

    def post_send(self, *args, **kwargs):
        pass

    def serialize_message(self, message, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        """
        unset the event object and close the file_handler.
        we can specify close_timeout to sleep for some time before closing the file handler.
        """
        if kwargs.get('close_timeout'):
            time.sleep(kwargs.get('close_timeout'))
        self._file_handler.close()

    @staticmethod
    def append_thread_id_to_file(file):
        parent_dir = (os.path.abspath(os.path.join(file, os.pardir)))
        file_with_ext = os.path.basename(file)
        file_name, ext = os.path.splitext(file_with_ext)
        file_with_thread_id = file_name + '-' + str(threading.current_thread().ident)
        final_file_path = os.path.join(parent_dir, '.'.join([file_with_thread_id, ext]))
        return final_file_path




















