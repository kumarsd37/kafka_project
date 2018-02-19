from abc import ABC, abstractmethod


class KafkaDAO(ABC):

    @abstractmethod
    def commit_offset(self, topic_partition_offset):
        """
        .. :function:: commit_offsets(self, topic_partition_offset)

        commit the offsets synchronously

        :param topic_partition_offset: TopicPartitionOffset object consists of topic, partition, offset
        :type topic_partition_offset: TopicPartitionOffset
        :return:  boolean value for success or failure
        :rtype: bool
        """

    @abstractmethod
    def get_all_topics_partitions_offset(self):
        """
        .. :function:: get_all_topics_partitions_offset(self)

        Get all topics partitions offsets
        """

    @abstractmethod
    def get_topic_all_partitions_offset(self, topic):
        """
        .. :function:: get_topic_all_partitions_offset(self, topic)

        Get all topic partitions offset

        :param topic: TopicPartitionOffset object with topic and partitions
        :type topic: topic name to get partitions and offsets
        :return: list of TopicPartitionOffset object
        :rtype: list(TopicPartitionOffset)
        """

    @abstractmethod
    def get_topic_partition_offset(self, topic_partition_offset):
        """
        .. :function:: get_topic_partition_offset(self, topic_partition_offset)

        Get the offset for the specified topic and partition

        :param topic_partition_offset: TopicPartitionOffset object with topic and partition
        :type topic_partition_offset: TopicPartitionOffset
        :return: record of TopicPartitionOffset
        :rtype: TopicPartitionOffset
        """