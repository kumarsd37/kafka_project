import logging

from kafka.errors import KafkaError

__author__ = 'pavan.tummalapalli'

import zlib
import os
from logging.handlers import RotatingFileHandler
from logging import addLevelName, NOTSET
from kafka import KafkaProducer
import logging.config


EVENT = 25

# scenario -1
class CustomLogger(logging.Logger):
    """
    custom logger to add additional logging levels and logging functions.
    """
    def __init__(self, name, level=NOTSET):
        super().__init__(name, level)

        addLevelName(EVENT, "EVENT")

    def event(self, msg, *args, **kwargs):
        if self.isEnabledFor(EVENT):
            self._log(EVENT, msg, args, **kwargs)



# scenario - 2
addLevelName(EVENT, "EVENT")
def event(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(EVENT):
        self._log(EVENT, message, args, **kws)


class ZippedRotatingFileHandler(RotatingFileHandler):

    def namer(self, name):
        """
        It will override base function to rename the filename with .gz extension.

        :param name: name of the file
        :type name: str
        :return: filename with .gz extension
        :rtype: str
        """
        return name + ".gz"

    def rotator(self, source, dest):
        """
        rotator will compress the source data and writes to destination.

        :param source: source of the file
        :type source: str
        :param dest: destination of the compressed file
        :type dest: str
        :return: None
        :rtype: None
        """
        with open(source, "rb") as sf:
            data = sf.read()
            compressed = zlib.compress(data, 9)
            with open(dest, "wb") as df:
                df.write(compressed)
        os.remove(source)


class KafkaLoggingHandler(logging.Handler):

    def __init__(self, hosts_list, topic, **kwargs):
        """
        constructor for kafka logging handler.

        :param hosts_list: bootstrap_servers
        :type hosts_list: union(str, list)
        :param topic: topic to send to logs
        :type topic: str
        :param kwargs: Additional kafka producer keyword arguments
        :type kwargs: dict
        """
        logging.Handler.__init__(self)

        self.kafka_producer = KafkaProducer(bootstrap_servers=hosts_list)
        self.key = kwargs.get('key', None)
        self.topic = topic
        self.close_timeout = kwargs.get('close_timeout', 3)

    def emit(self, record):
        if record.levelno == 25:
            try:
                msg = self.format(record)
                msg = msg.encode("utf-8")
                future = self.kafka_producer.send(topic=self.topic, value=msg, key=self.key)
                self.kafka_producer.flush()
            except (KafkaError, Exception) as exc:
                raise exc
            except:
                self.handleError(record)
        else:
            return

    def close(self):
        if self.kafka_producer is not None:
            self.kafka_producer.close(timeout=self.close_timeout)
        logging.Handler.close(self)
