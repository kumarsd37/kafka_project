__author__ = 'pavan.tummalapalli'

from abc import ABC, abstractmethod


class AbstractConsumer(ABC):
    """
    Abstract consumer for all messaging clients.
    """

    @abstractmethod
    def consume(self, *args, **kwargs):
        """ consumes the messages """

    @abstractmethod
    def close(self, *args, **kwargs):
        """ close the consumer """

    @abstractmethod
    def serialize_message(self, message, *args, **kwargs):
        """ serialize the message"""

    @abstractmethod
    def deserialize_message(self, message, *args, **kwargs):
        """ deserialize the message """

