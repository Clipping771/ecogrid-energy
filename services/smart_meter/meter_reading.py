import uuid
from datetime import datetime


class MeterReading:
    """Represents a single reading from a smart meter device."""

    def __init__(self, device_id: str, energy_kwh: float, reading_type: str):
        self.device_id = device_id
        self.energy_kwh = energy_kwh
        self.reading_type = reading_type  # 'generation' or 'consumption'
        self.timestamp = datetime.utcnow().isoformat()
        self.reading_id = str(uuid.uuid4())

    def to_dict(self):
        return {
            "reading_id": self.reading_id,
            "device_id": self.device_id,
            "energy_kwh": self.energy_kwh,
            "reading_type": self.reading_type,
            "timestamp": self.timestamp
        }