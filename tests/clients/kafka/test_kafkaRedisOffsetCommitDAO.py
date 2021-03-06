from unittest import TestCase

from framework.utils.caching.redis_pool import RedisPoolConnection
from framework.clients.kafka import (KafkaRedisOffsetCommitDAO , TopicPartitionOffset)


class TestKafkaRedisOffsetCommitDAO(TestCase):

    def setUp(self):

        config = {
            'host': 'localhost',
            'port': 6379,
            'password': None,
            'db_number': None,
            'max_connections': 2
        }

        try:
            self.redis_connection = RedisPoolConnection(**config)
        except Exception as exc:
            raise exc

        consumer_group = 'TESTING_BLOB_CG'
        namespace = 'testing'
        delimiter = ':'

        self.kafka_redis_offset_commit_dao = KafkaRedisOffsetCommitDAO(self.redis_connection, consumer_group=consumer_group, namespace=namespace, delimiter=delimiter)

    def tearDown(self):
        del self.kafka_redis_offset_commit_dao
        del self.redis_connection

    def test_commit_offset(self):
        tpo = TopicPartitionOffset('TESTING', 0, 0)
        response = self.kafka_redis_offset_commit_dao.commit_offset(tpo)
        self.assertTrue(response)

    def test_get_all_topics_partitions_offset(self):
        tpo0 = TopicPartitionOffset('TESTING', 0, 0)
        tpo1 = TopicPartitionOffset('TESTING', 1, 0)
        tpo2 = TopicPartitionOffset('TESTING', 2, 0)
        for i in range(0, 3):
            obj = eval('tpo'+str(i))
            response = self.kafka_redis_offset_commit_dao.commit_offset(obj)
            self.assertTrue(response)
        topic_partition_offset_list = self.kafka_redis_offset_commit_dao.get_all_topics_partitions_offset()
        self.assertGreaterEqual(len(topic_partition_offset_list), 3)

    def test_get_topic_all_partitions_offset(self):
        tpo0 = TopicPartitionOffset('TESTING', 0, 0)
        tpo1 = TopicPartitionOffset('TESTING', 1, 0)
        tpo2 = TopicPartitionOffset('TESTING', 2, 0)
        for i in range(0, 3):
            obj = eval('tpo' + str(i))
            response = self.kafka_redis_offset_commit_dao.commit_offset(obj)
            self.assertTrue(response)
        topic = 'TESTING'
        topic_partition_offset_list = self.kafka_redis_offset_commit_dao.get_topic_all_partitions_offset(topic)
        self.assertGreaterEqual(len(topic_partition_offset_list), 3)

    def test_get_topic_partition_offset(self):
        tpo0 = TopicPartitionOffset('TESTING', 0, 0)
        response = self.kafka_redis_offset_commit_dao.commit_offset(tpo0)
        self.assertTrue(response)
        topic_partition_offset = self.kafka_redis_offset_commit_dao.get_topic_partition_offset(tpo0)
        self.assertEqual(topic_partition_offset.offset, tpo0.offset+1)
