__author__ = 'pavan.tummalapalli'

import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError

from framework.abstract_client import AbstractProducer

logger = logging.getLogger(__name__)


class Producer(AbstractProducer):

    def __init__(self, *args, **kwargs):
        """
        The producer is thread safe and sharing a single producer instance across
        threads will generally be faster than having multiple instances.

        sample configuration file:
        ::

            configs = {

                'future_timeout': 5,
                'close_timeout': 5,
                'client_config': {
                    'bootstrap_servers': '172.16.15.227:9092',
                    'client_id': '_'.join([TOPIC, 'producer_client']),
                    'acks': 1,
                    'retries': 1,
                    'batch_size': 16384,
                    'linger_ms': 5,
                    'buffer_memory': 33554432,
                    'connections_max_idle_ms': 9 * 60 * 1000,
                    'max_block_ms': 60000,
                    'max_request_size': 1048576,
                    'metadata_max_age_ms': 300000,
                    'retry_backoff_ms': 100,
                    'request_timeout_ms': 30000,
                    'max_in_flight_requests_per_connection': 5,
                }
            }


        """
        assert kwargs, 'unrecognized keyword arguments'
        self.configs = kwargs
        self.topic = self.configs.get('topic')
        assert self.configs.get('client_config'), 'unrecognized client_config'

        self._success_callback = kwargs.get('success_callback')
        self._failure_callback = kwargs.get('failure_callback')

        try:
            self.producer_client = KafkaProducer(**self.configs.get('client_config'))
        except KafkaError as e:
            raise e

    def pre_send(self, *args, **kwargs):
        pass

    def send(self, message):
        """ sends the message to specified topic """
        try:
            meta_data = self.send_sync(topic=self.topic, key=None, value=message, partition=None, timestamp_ms=None)
            return meta_data
        except (KafkaTimeoutError, KafkaError) as exc:
            raise exc

    def _send(self, topic=None, key=None, value=None, partition=None, timestamp_ms=None):
        """
        publish the message to topic synchronously

        :param topic: topic where the message will be published
        :type topic: str
        :param key: a key to associate with the message. Can be used to determine which partition to send the message to. If partition is None (and producer’s partitioner config is left as default), then messages with the same key will be delivered to the same partition (but if key is None, partition is chosen randomly). Must be type bytes, or be serializable to bytes via configured key_serializer
        (optional, default: None)
        :type key: int, optional
        :param value: message value. Must be type bytes, or be serializable to bytes via configured value_serializer. If value is None, key is required and message acts as a ‘delete’.
        :type value: optional, byte
        :param partition: optionally specify a partition. If not set, the partition will be selected using the configured ‘partitioner’
        :type partition: int, optional
        :param timestamp_ms: epoch milliseconds (from Jan 1 1970 UTC) to use as the message timestamp. Defaults to current time
        :type timestamp_ms: int, optional
        :return: resolves to RecordMetadata
        :rtype:  FutureRecordMetadata
        :raises KafkaError: if unable to send
        :raises KafkaTimeoutError: if timeout has occurred
        """

        try:
            future = self.producer_client.send(topic=topic, key=key, value=value, partition=partition, timestamp_ms=timestamp_ms)
            return future
        except (KafkaError, KafkaTimeoutError) as e:
            logger.error(e, exc_info=True)
            raise e

    def send_sync(self, topic=None, key=None, value=None, partition=None, timestamp_ms=None):
        """
        publish the message to topic synchronously and return meta_data or if it fails to send,
        it will raise an exception

        :param topic: topic where the message will be published
        :type topic: str
        :param key: a key to associate with the message. Can be used to determine which partition to send the message to. If partition is None (and producer’s partitioner config is left as default), then messages with the same key will be delivered to the same partition (but if key is None, partition is chosen randomly). Must be type bytes, or be serializable to bytes via configured key_serializer
        :type key: int, optional
        :param value: message value. Must be type bytes, or be serializable to bytes via configured value_serializer. If value is None, key is required and message acts as a ‘delete’
        :type value: optional, byte
        :param partition: optionally specify a partition. If not set, the partition will be selected using the configured ‘partitioner’
        :type partition: int, optional
        :param timestamp_ms: epoch milliseconds (from Jan 1 1970 UTC) to use as the message timestamp. Defaults to current time
        :type timestamp_ms: int, optional
        :return: resolves to RecordMetadata
        :rtype:  FutureRecordMetadata
        :raises KafkaError: if unable to send
        :raises KafkaTimeoutError: if timeout has occurred
        """
        try:
            future = self._send(topic=topic, key=key, value=value, partition=partition, timestamp_ms=timestamp_ms)
            meta_data = future.get(timeout=self.configs.get('future_timeout') or 3)
            logger.info('sent to oubound topic {}, {}, {}'.format(meta_data.topic, meta_data.partition, meta_data.offset))
            return meta_data
        except (KafkaTimeoutError, KafkaError) as e:
            logger.error(e, exc_info=True)
            raise e

    def send_async(self, topic=None, key=None, value=None, partition=None, timestamp_ms=None):
        """
        publish the message to kafka_client asynchronously. if success and failure callback handlers exists,
        it will add to the FutureRecordMetadata

        :param topic: topic where the message will be published
        :type topic: str
        :param key: a key to associate with the message. Can be used to determine which partition to send the message to. If partition is None (and producer’s partitioner config is left as default), then messages with the same key will be delivered to the same partition (but if key is None, partition is chosen randomly). Must be type bytes, or be serializable to bytes via configured key_serializer
        :type key: int, optional
        :param value: message value. Must be type bytes, or be serializable to bytes via configured value_serializer. If value is None, key is required and message acts as a ‘delete’
        :type value: byte, optional
        :param partition: optionally specify a partition. If not set, the partition will be selected using the configured ‘partitioner’
        :type partition: int, optional
        :param timestamp_ms: epoch milliseconds (from Jan 1 1970 UTC) to use as the message timestamp. Defaults to current time
        :type timestamp_ms: int, optional
        :return: resolves to RecordMetadata
        :rtype:  FutureRecordMetadata
        :raises KafkaError: if unable to send
        :raises KafkaTimeoutError: if timeout has occurred
        """

        future = self._send(topic=topic, key=key, value=value, partition=partition, timestamp_ms=timestamp_ms)
        if self._success_callback and self._failure_callback:
            future.add_callback(self._success_callback)
            future.add_callback(self._failure_callback)

    def post_send(self, *args, **kwargs):
        pass

    def flush(self, timeout=None):
        """
        Invoking this method makes all buffered records immediately available to send
        (even if linger_ms is greater than 0) and blocks on the completion of the requests
        associated with these records. The post-condition of flush() is that any previously sent
        record will have completed (e.g. Future.is_done() == True). A request is considered
        completed when either it is successfully acknowledged according to the ‘acks’ configuration
        for the producer, or it results in an error.
        Other threads can continue sending messages while one thread is blocked waiting for a flush call to complete; however, no guarantee is made about the completion of messages sent after the flush call begins

        :param timeout: timeout in seconds to wait for completion
        :type timeout: float, optional
        :raises KafkaError: if unable to send
        :raises KafkaTimeoutError: if timeout has occurred
        """
        try:
            self.producer_client.flush(timeout=timeout)
        except (KafkaTimeoutError, KafkaError) as e:
            raise e

    def serialize_message(self, message, *args, **kwargs):
        """ serialize the message """
        pass

    def close(self):
        """ close the producer"""
        try:
            logger.info('closing producer...')
            self.producer_client.close(timeout=self.configs.get('close_timeout') or 5)
        except KafkaError as e:
            raise e


# todo : keys , partitions for sending in kafka_client need to initialing the producer client


