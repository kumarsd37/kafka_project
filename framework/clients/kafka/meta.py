__author__ = 'pavan.tummalapalli'

from collections import namedtuple

TopicMetaData = namedtuple('TopicMetaData', 'topic', 'partition', 'offset', 'error')
TopicData = namedtuple('TopicData', 'topic', 'partition', 'offset', 'message', 'error')

