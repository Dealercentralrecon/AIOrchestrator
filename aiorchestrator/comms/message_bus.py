class MessageBus:
    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, topic, callback):
        self.listeners[topic].append(callback)

    def publish(self, topic, message):
        for callback in self.listeners[topic]:
            callback(message)
