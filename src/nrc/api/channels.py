from base64 import b64encode

import pika


class QueueChannel:
    def __init__(self, params):
        self.params = params
        # connection objects
        self.connection = None
        self.channel = None
        # exchange params
        self.exchange = None
        self.exchange_type = None
        self.routing_key = None

    def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.params))
            self.channel = self.connection.channel()

    def set_exchange(self, exchange, exchange_type="topic"):
        self.exchange = exchange
        self.exchange_type = exchange_type

    def set_routing_key_encoded(self, filter_list):
        encoded_topics = []
        for filter_dict in filter_list:
            filter_val = list(filter_dict.values())[0]
            encoded_val = b64encode(filter_val.encode())
            encoded_topics.append(encoded_val.decode())
        self.routing_key = ".".join(encoded_topics)

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

    def send(self, msg):
        """put the message of the RabbitMQ queue."""
        self.connect()
        self.channel.exchange_declare(
            exchange=self.exchange, exchange_type=self.exchange_type
        )
        # msg = dumps(msg, cls=DjangoJSONEncoder)
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=msg,
            properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
        )
