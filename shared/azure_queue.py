from azure.storage.queue import QueueClient
from azure.core.exceptions import ResourceExistsError
import json

class AzureQueue:
    def __init__(self, connection_string, queue_name):
        self.connection_string = connection_string
        self.queue_name = queue_name
        self.queue_client = QueueClient.from_connection_string(connection_string, queue_name)

    def create_queue(self):
        try:
            self.queue_client.create_queue()
        except ResourceExistsError:
            pass

    def send_message(self, message):
        payload = json.dumps(message)
        self.queue_client.send_message(payload)

    def receive_messages(self, num_messages=1):
        messages = self.queue_client.receive_messages(num_messages=num_messages)
        return [json.loads(message.content) for message in messages]

    def delete_message(self, message):
        self.queue_client.delete_message(message)
