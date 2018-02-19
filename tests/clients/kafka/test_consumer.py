from unittest import TestCase


from framework.clients.kafka import TopicPartitionOffset
from kafka.errors import KafkaError, CommitFailedError
from kafka.producer.future import RecordMetadata

from framework.clients.kafka import Producer
from framework.clients.kafka import Consumer
from tests.testutils import random_string


class TestConsumer(TestCase):

    consumer_settings = {
                       "topics": ["testing"],
                       "max_records": 1,
                       "poll_timeout": 100,
                       "close_timeout": 5,
                       "enable_external_commit": False,
                       "external_commit_config": {
                           "redis": {
                               "namespace": "kafka",
                               "delimiter": ":",
                               "client_config": {
                                   "host": "localhost",
                                   "port": 6379,
                                   "password": False,
                                   "db_number": False,
                                   "max_connections": 2
                               }
                           }
                       },
                       "client_config": {
                           "bootstrap_servers": "localhost:9092",
                           "group_id": "ARTICLE_CG_GRP",
                           "enable_auto_commit": False,
                           "session_timeout_ms": 27000,
                           "heartbeat_interval_ms": 9000,
                           "auto_offset_reset": "earliest",
                       }
                   }

    producer_settings = {
        "topic": "testing",
        "future_timeout": 5,
        "close_timeout": 5,
        "success_callback": None,
        "failure_callback": None,
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

    def test_subscribe(self):
        pass

    def test_seek(self):
        pass

    def test_assignment(self):
        topic = random_string(7)

        __class__.producer_settings['topic'] = topic
        __class__.consumer_settings['topics'] = [topic]

        __class__.consumer_settings['enable_external_commit'] = True
        __class__.consumer_settings['client_config']['enable_auto_commit'] = False

        try:
            self.producer_client = Producer(**__class__.producer_settings)
        except KafkaError as exc:
            raise exc

        msg = b'Testing message'
        meta_data = self.producer_client.send(msg)
        self.producer_client.close()
        self.assertIsInstance(meta_data, RecordMetadata)
        self.assertIsNotNone(meta_data.offset)
        self.assertIsInstance(meta_data.offset, int)

        try:
            self.consumer_client = Consumer(**__class__.consumer_settings)
        except KafkaError as exc:
            raise exc

        try:
            messages = self.consumer_client.consume()
            assignments = self.consumer_client.assignment()
            self.assertGreater(len(assignments), 0)
        except CommitFailedError as exc:
            raise exc
        self.consumer_client.close()

    def test_beginning_offsets(self):
        pass

    def test_seek_to_beginning(self):
        pass

    def test_pre_consume(self):
        pass

    def test_consume(self):
        pass

    def test_external_commit(self):
        topic = random_string(7)

        __class__.producer_settings['topic'] = topic
        __class__.consumer_settings['topics'] = [topic]

        __class__.consumer_settings['enable_external_commit'] = True
        __class__.consumer_settings['client_config']['enable_auto_commit'] = False

        try:
            self.producer_client = Producer(**__class__.producer_settings)
        except KafkaError as exc:
            raise exc

        msg = b'Testing message'
        meta_data = self.producer_client.send(msg)
        self.producer_client.close()
        self.assertIsInstance(meta_data, RecordMetadata)
        self.assertIsNotNone(meta_data.offset)
        self.assertIsInstance(meta_data.offset, int)

        producer_offset = meta_data.offset

        try:
            self.consumer_client = Consumer(**__class__.consumer_settings)
        except KafkaError as exc:
            raise exc

        try:
            messages = self.consumer_client.consume()
            for msg in messages:
                tpo = TopicPartitionOffset(msg.topic, msg.partition, msg.offset)
                self.consumer_client.commit(tpo)
                topic_partition_offset = self.consumer_client.last_committed_offset_from_external(tpo)
                print(topic_partition_offset)
            self.assertEqual(topic_partition_offset.offset, producer_offset + 1)

        except CommitFailedError as exc:
            raise exc
        self.consumer_client.close()

    def test_internal_commit(self):
        topic = random_string(7)

        __class__.producer_settings['topic'] = topic
        __class__.consumer_settings['topics'] = [topic]

        __class__.consumer_settings['enable_external_commit'] = False
        __class__.consumer_settings['client_config']['enable_auto_commit'] = False

        try:
            self.producer_client = Producer(**__class__.producer_settings)
        except KafkaError as exc:
            raise exc

        msg = b'Testing message'
        meta_data = self.producer_client.send(msg)
        self.producer_client.close()
        self.assertIsInstance(meta_data, RecordMetadata)
        self.assertIsNotNone(meta_data.offset)
        self.assertIsInstance(meta_data.offset, int)

        producer_offset = meta_data.offset

        try:
            self.consumer_client = Consumer(**__class__.consumer_settings)
        except KafkaError as exc:
            raise exc

        try:
            messages = self.consumer_client.consume()
            for msg in messages:
                tpo = TopicPartitionOffset(msg.topic, msg.partition, msg.offset)
                self.consumer_client.commit(tpo,)
                consumer_offset = self.consumer_client.last_committed_offset(tpo)
            self.assertEqual(consumer_offset, producer_offset+1)

        except CommitFailedError as exc:
            raise exc
        self.consumer_client.close()

    def test_commit_async(self):
        topic = random_string(7)

        __class__.producer_settings['topic'] = topic
        __class__.consumer_settings['topics'] = [topic]

        try:
            self.producer_client = Producer(**__class__.producer_settings)
        except KafkaError as exc:
            raise exc

        msg = b'Testing message'
        meta_data = self.producer_client.send(msg)
        self.producer_client.close()
        self.assertIsInstance(meta_data, RecordMetadata)
        self.assertIsNotNone(meta_data.offset)
        self.assertIsInstance(meta_data.offset, int)

        try:
            self.consumer_client = Consumer(**__class__.consumer_settings)
        except KafkaError as exc:
            raise exc

        def callback(offsets, response):
            pass

        try:
            messages = self.consumer_client.consume()
            for msg in messages:
                tpo = TopicPartitionOffset(msg.topic, msg.partition, msg.offset)
                self.consumer_client.commit_async(tpo, callback=callback)
        except CommitFailedError as exc:
            raise exc
        self.consumer_client.close()

    def test_commit(self):
        topic = random_string(7)

        __class__.producer_settings['topic'] = topic
        __class__.consumer_settings['topics'] = [topic]

        try:
            self.producer_client = Producer(**__class__.producer_settings)
        except KafkaError as exc:
            raise exc

        msg = b'Testing message'
        meta_data = self.producer_client.send(msg)
        self.producer_client.close()
        self.assertIsInstance(meta_data, RecordMetadata)
        self.assertIsNotNone(meta_data.offset)
        self.assertIsInstance(meta_data.offset, int)

        try:
            self.consumer_client = Consumer(**__class__.consumer_settings)
        except KafkaError as exc:
            raise exc

        try:
            messages = self.consumer_client.consume()
            for msg in messages:
                tpo = TopicPartitionOffset(msg.topic, msg.partition, msg.offset)
                self.consumer_client.commit(tpo)
        except CommitFailedError as exc:
            raise exc
        self.consumer_client.close()

    def test_partitions_for_topic(self):

        topic = random_string(7)

        __class__.producer_settings['topic'] = topic
        __class__.consumer_settings['topics'] = [topic]

        try:
            self.producer_client = Producer(**__class__.producer_settings)
        except KafkaError as exc:
            raise exc

        msg = b'Testing message'
        meta_data = self.producer_client.send(msg)
        self.assertIsInstance(meta_data, RecordMetadata)
        self.assertIsNotNone(meta_data.offset)
        self.assertIsInstance(meta_data.offset, int)

        try:
            self.consumer_client = Consumer(**__class__.consumer_settings)
        except KafkaError as exc:
            raise exc

        partitions = self.consumer_client.partitions_for_topic(topic)

        self.assertGreaterEqual(len(partitions), 0)
        self.consumer_client.close()
