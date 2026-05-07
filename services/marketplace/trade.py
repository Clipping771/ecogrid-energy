import uuid
from datetime import datetime


class Trade:
    """Represents a confirmed energy trade between buyer and seller."""

    def __init__(self, listing, buyer_id: str, quantity_kwh: float):
        self.trade_id = str(uuid.uuid4())
        self.listing_id = listing.listing_id
        self.seller_id = listing.seller_id
        self.buyer_id = buyer_id
        self.quantity_kwh = quantity_kwh
        self.price_per_kwh = listing.price_per_kwh
        self.total_cost = round(quantity_kwh * listing.price_per_kwh, 2)
        self.status = "confirmed"
        self.confirmed_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "trade_id": self.trade_id,
            "listing_id": self.listing_id,
            "seller_id": self.seller_id,
            "buyer_id": self.buyer_id,
            "quantity_kwh": self.quantity_kwh,
            "price_per_kwh": self.price_per_kwh,
            "total_cost": self.total_cost,
            "status": self.status,
            "confirmed_at": self.confirmed_at
        }