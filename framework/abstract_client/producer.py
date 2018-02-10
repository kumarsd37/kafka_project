__author__ = 'pavan.tummalapalli'

from abc import ABC
from abc import abstractmethod


class AbstractProducer(ABC):
    """
    Abstract producer for all messaging clients.
    """

    @abstractmethod
    def send(self, message, **kwargs):
        """ send the message."""

    @abstractmethod
    def close(self, *args, **kwargs):
        """ close the producer. if timeout is specified for the producer client pass the timeout
            option. otherwise sleep up to timeout value.
        """
    @abstractmethod
    def serialize_message(self, message, *args, **kwargs):
        """ serialize the message"""

    @abstractmethod
    def deserialize_message(self, message, *args, **kwargs):
        """ deserialize the message """


