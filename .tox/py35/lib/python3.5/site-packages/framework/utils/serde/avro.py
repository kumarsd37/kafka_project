import io
import fastavro as avro


def write(records=None, schema=None):
    """
    serialize message with schema.

    :param schema: avro schema
    :type dict
    :param records: list of messages
    :type message: list
    :return serialized message: serialized message
    :rtype bytes
    """
    try:
        out = io.BytesIO()
        avro.writer(out, schema, records)
        return out.getvalue()
    except Exception as e:
        raise e


def read(records=None, schema=None):
    """
    deserialize message using schema

    :param schema: avro schema
    :type dict
    :param message: message to be serialized
    :type message: string
    :return: deserialized message: avro deserialized message

    """
    try:
        op = io.BytesIO(records)
        reader = avro.reader(op, reader_schema=schema)
        return reader
    except Exception as e:
        raise e









