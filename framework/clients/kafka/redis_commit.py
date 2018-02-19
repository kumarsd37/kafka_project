from .dao import KafkaDAO
from .meta import TopicPartitionOffset

from framework.utils.date_utils import current_time_in_milliseconds

import logging

logger = logging.getLogger(__name__)


class KafkaRedisOffsetCommitDAO(KafkaDAO):

    def __init__(self, pooled_redis_connection, namespace=None, delimiter=None):
        """
        :param pooled_redis_connection: pooled mysql connection client
        :type pooled_redis_connection: MySQLPool
        """
        self.pooled_redis_connection = pooled_redis_connection
        self.namespace = namespace
        self.delimiter = delimiter or ':'

    def commit_offset(self, topic_partition_offset):
        try:
            key = '-'.join([topic_partition_offset.topic, str(topic_partition_offset.partition)])
            value = {
                'offset': topic_partition_offset.offset+1,
                'last_committed_time': current_time_in_milliseconds()
            }
            response = self.pooled_redis_connection.hm_set(name=key, hash_map=value, namespace=self.namespace, delimiter=self.delimiter)
        except (ConnectionError, TimeoutError, Exception) as exc:
            logger.exception(str(exc))
            raise exc
        return response

    def get_all_topics_partitions_offset(self):
        """
        Get all topics partitions offsets

        :return: list of TopicPartitionOffset object
        :rtype: list(TopicPartitionOffset)
        """

        try:
            if self.namespace:
                namespace = self.namespace + '*'
            else:
                namespace = '*'
            keys_with_values = self.pooled_redis_connection.get_all_hash_maps(regex=namespace + '*')
            topic_partition_offset_list = self.create_topic_partition_list(keys_with_values)
            return topic_partition_offset_list

        except (ConnectionError, TimeoutError, Exception) as exc:
            logger.exception(str(exc))
            raise exc
        return topic_partition_offset_list

    def get_topic_all_partitions_offset(self, topic):

        """
        Get all topic partitions offset

        :param topic: topic name to get partitions and offsets
        :type topic: str
        :return: list of TopicPartitionOffset object
        :rtype: list(TopicPartitionOffset)
        """

        try:
            key_with_or_without_namespace = [x for x in [self.namespace, topic] if x]
            key = self.delimiter.join(key_with_or_without_namespace)
            keys_with_values = self.pooled_redis_connection.get_all_hash_maps(regex=key + '*')
            topic_partition_offset_list = self.create_topic_partition_list(keys_with_values)
        except (ConnectionError, TimeoutError, Exception) as exc:
            logger.exception(str(exc))
            raise exc
        return topic_partition_offset_list

    def get_topic_partition_offset(self, topic_partition_offset):
        """
        Get the offset for the specified topic and partition

        :param topic_partition_offset: TopicPartitionOffset object with topic and partition
        :type topic_partition_offset: TopicPartitionOffset
        :return: record of TopicPartitionOffset
        :rtype: TopicPartitionOffset
        """
        topic = topic_partition_offset.topic
        partition = topic_partition_offset.partition
        key = '-'.join([topic, str(partition)])
        value = self.pooled_redis_connection.hm_get(name=key, namespace=self.namespace, delimiter=self.delimiter)

        offset = None
        if value:
            logger.debug('offset with last committed time is {}'.format(value))
            offset = int(value.get('offset'))
        tpo = TopicPartitionOffset(topic, partition, offset)
        return tpo

    def create_topic_partition_list(self, keys_with_values):
        """
        create topic partition offset list

        :param keys_with_values: list of tuple
        :type keys_with_values: list(tuple(key, value))
        :return: list of TopicPartitionOffset objects consists of topic partition and offset
        :rtype: list(TopicPartitionOffset)
        """
        topic_partition_offset_list = list()

        for (key, value) in keys_with_values:
            key_with_or_without_namespace_delimiter = key.split(self.delimiter)
            logger.debug('key with or without namespace delimiter')
            if len(key_with_or_without_namespace_delimiter) > 1:
                key = key_with_or_without_namespace_delimiter[1]
            else:
                key = key_with_or_without_namespace_delimiter[0]
            topic, partition = key.split('-')

            offset = None
            if value:
                logger.debug('offset with last committed time is {}'.format(value))
                offset = value.get('offset')
            tpo = TopicPartitionOffset(topic, int(partition), int(offset))
            topic_partition_offset_list.append(tpo)

        return topic_partition_offset_list
