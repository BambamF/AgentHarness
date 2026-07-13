
class Artefact:
    def __init__(self, producer, exec_id, timestamp, payload):
        self.artefact_id = 0
        self.execution_id = exec_id
        self.producer = producer
        self.producer_state = producer.current_state
        self.timestamp = timestamp
        self.confidence = 0
        self.metadata = None
        self.payload = payload
    
    def get_artefact_id(self):
        return self.artefact_id
