from unittest import TestCase

from kafka.errors import KafkaError
from kafka.producer.future import RecordMetadata

from framework.clients.kafka import Producer
from tests.testutils import random_string


class TestProducer(TestCase):

    def setUp(self):

        def success_callback(metadata, *args, **kwargs):
            self.assertIsInstance(metadata, RecordMetadata)
            self.assertIsNotNone(metadata.offset)
            self.assertIsInstance(metadata.offset, int)

        def failure_callback(*args, **kwargs):
            print('failure')
            print(args)
            print(kwargs)

        topic = random_string(7)

        kwargs = {
            "topic": topic,
            "future_timeout": 5,
            "close_timeout": 5,
            "success_callback": success_callback,
            "failure_callback": failure_callback,
            "client_config": {
                "bootstrap_servers": "localhost:9092",
                "acks": 1,
                "retries": 1,
                "batch_size": 16384,
                "linger_ms": 5,
                "buffer_memory": 33554432,
                "connections_max_idle_ms": 54000,
                "max_block_ms": 60000,
                "max_request_size": 1048576,
                "metadata_max_age_ms": 300000,
                "retry_backoff_ms": 100,
                "request_timeout_ms": 30000,
                "max_in_flight_requests_per_connection": 5
            }
        }

        try:
            self.producer_client = Producer(**kwargs)
        except KafkaError as exc:
            raise exc

    def tearDown(self):
        self.producer_client.close()

    def test_send(self):
        msg = b'Testing message'
        metadata = self.producer_client.send(msg)
        self.assertIsInstance(metadata, RecordMetadata)
        self.assertIsNotNone(metadata.offset)
        self.assertIsInstance(metadata.offset, int)

    def test_send_sync(self):
        msg = b'Testing message'
        metadata = self.producer_client.send(msg)
        self.assertIsInstance(metadata, RecordMetadata)
        self.assertIsNotNone(metadata.offset)
        self.assertIsInstance(metadata.offset, int)

    def test_send_async(self):
        topic = 'TESTING'
        msg = b'Testing message'
        self.producer_client.send_async(topic=topic, value=msg)


