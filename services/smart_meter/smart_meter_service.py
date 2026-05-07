import uuid
from datetime import datetime
from services.smart_meter.meter_reading import MeterReading


class SmartMeterService:
    """
    Smart Meter Integration Service.
    Ingests raw meter readings, validates them, and publishes
    EnergyAvailableEvents for the Marketplace to consume.
    """

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.processed_readings = {}

    def ingest_reading(self, device_id: str, energy_kwh: float, reading_type: str):
        """Validate and process an incoming meter reading."""

        # Validate input
        if energy_kwh < 0:
            raise ValueError(f"Invalid energy reading: {energy_kwh}. Must be non-negative.")
        if reading_type not in ("generation", "consumption"):
            raise ValueError(f"Invalid reading type: {reading_type}")

        reading = MeterReading(device_id, energy_kwh, reading_type)
        self.processed_readings[reading.reading_id] = reading

        print(f"[SmartMeter] Reading ingested: Device {device_id} | "
              f"{energy_kwh} kWh | Type: {reading_type}")

        # Publish event if surplus energy is being generated
        if reading_type == "generation" and energy_kwh > 0:
            self._publish_energy_available_event(reading)

        return reading

    def _publish_energy_available_event(self, reading: MeterReading):
        """Publish an EnergyAvailableEvent to the event bus."""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "EnergyAvailableEvent",
            "correlation_id": reading.reading_id,
            "device_id": reading.device_id,
            "available_kwh": reading.energy_kwh,
            "timestamp": reading.timestamp
        }
        self.event_bus.publish("energy_available", event)
        print(f"[SmartMeter] Published EnergyAvailableEvent for device {reading.device_id}")