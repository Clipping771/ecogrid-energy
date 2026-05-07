import uuid
from datetime import datetime


class Listing:
    """Represents a seller's offer to sell energy."""

    def __init__(self, seller_id: str, available_kwh: float, price_per_kwh: float):
        self.listing_id = str(uuid.uuid4())
        self.seller_id = seller_id
        self.available_kwh = available_kwh
        self.price_per_kwh = price_per_kwh
        self.status = "open"
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "listing_id": self.listing_id,
            "seller_id": self.seller_id,
            "available_kwh": self.available_kwh,
            "price_per_kwh": self.price_per_kwh,
            "status": self.status,
            "created_at": self.created_at
        }