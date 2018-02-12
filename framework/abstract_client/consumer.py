__author__ = 'pavan.tummalapalli'

from abc import ABC, abstractmethod


class AbstractConsumer(ABC):
    """
    Abstract consumer for all messaging clients.
    """

    @abstractmethod
    def pre_consume(self, *args, **kwargs):
        """ operations to be performed before consume method call """

    @abstractmethod
    def consume(self, *args, **kwargs):
        """ consumes the messages """

    @abstractmethod
    def post_consume(self, *args, **kwargs):
        """ operations to be performed after consume method call """

    @abstractmethod
    def close(self, *args, **kwargs):
        """ close the consumer """

    @abstractmethod
    def deserialize_message(self, message, *args, **kwargs):
        """ deserialize the message """

