class EventBus:
    """
    Simple in-memory event bus simulating Apache Kafka.
    In production this would be replaced with a real Kafka client.
    """

    def __init__(self):
        self.subscribers = {}
        self.event_log = []

    def subscribe(self, topic: str, handler):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)

    def publish(self, topic: str, event: dict):
        self.event_log.append({"topic": topic, "event": event})
        if topic in self.subscribers:
            for handler in self.subscribers[topic]:
                handler(event)