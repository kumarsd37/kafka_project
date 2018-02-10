__author__ = 'pavan.tummalapalli'

import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError

from abstract_client import AbstractProducer

logger = logging.getLogger(__name__)


class Producer(AbstractProducer):

    def __init__(self, *args, **kwargs):
        """
        The producer is thread safe and sharing a single producer instance across
        threads will generally be faster than having multiple instances.

        sample configuration file:
        ::

            configs = {

                'response_timeout': 5,
                'connection_timeout': 5,
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

        :keyword Arguments:

        """
        assert kwargs, 'unrecognized keyword arguments'
        self.configs = kwargs
        assert self.configs.get('client_config'), 'unrecognized client_config'
        try:
            self.producer_client = KafkaProducer(**self.configs.get('client_config'))
        except KafkaError as e:
            raise e

    def send(self, topic=None, key=None , value=None):
        if topic is None:
            raise KafkaError('topic should not be none')
        try:
            future = self.producer_client.send(topic, key=key, value=value)
            meta_data = future.get(timeout=self.configs.get('future_timeout') or 3)
            logger.info('sent to oubound topic {}, {}, {}'.format(meta_data.topic, meta_data.partition, meta_data.offset))
            return meta_data
        except KafkaError as e:
            logger.error(e, exc_info=True)
            raise e

    def flush(self, timeout=None):
        try:
            self.producer_client.flush(timeout=timeout)
        except KafkaError as e:
            raise e

    def serialize_message(self, message, *args, **kwargs):
        pass

    def deserialize_message(self, message, *args, **kwargs):
        pass

    def close(self):
        try:
            logger.info('closing producer...')
            self.producer_client.close(timeout=self.configs.get('close_timeout') or 5)
        except KafkaError as e:
            raise e


