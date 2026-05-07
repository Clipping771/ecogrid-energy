import uuid
from datetime import datetime
from services.marketplace.listing import Listing
from services.marketplace.trade import Trade


class MarketplaceService:
    """
    Marketplace Service.
    Manages energy listings and matches buyers with sellers.
    Publishes TradeConfirmedEvents for the Settlement service.
    """

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.listings = {}
        self.trades = {}
        self.processed_event_ids = set()

        # Subscribe to energy available events from Smart Meter service
        self.event_bus.subscribe("energy_available", self.handle_energy_available)
        # Subscribe to settlement failure events
        self.event_bus.subscribe("settlement_failed", self.handle_settlement_failed)

    def handle_energy_available(self, event: dict):
        """Handle an EnergyAvailableEvent from the Smart Meter service."""
        event_id = event["event_id"]

        # Idempotency check — skip if already processed
        if event_id in self.processed_event_ids:
            print(f"[Marketplace] Duplicate event {event_id} skipped.")
            return

        self.processed_event_ids.add(event_id)

        # Create a listing from the energy available event
        seller_id = f"seller_{event['device_id']}"
        listing = Listing(
            seller_id=seller_id,
            available_kwh=event["available_kwh"],
            price_per_kwh=0.15
        )
        self.listings[listing.listing_id] = listing
        print(f"[Marketplace] New listing created: {listing.listing_id} | "
              f"{listing.available_kwh} kWh @ ${listing.price_per_kwh}/kWh")

    def place_bid(self, buyer_id: str, requested_kwh: float):
        """
        A buyer places a bid for energy.
        Finds the best available listing and confirms a trade.
        """
        # Find an open listing with sufficient energy
        matching_listing = None
        for listing in self.listings.values():
            if listing.status == "open" and listing.available_kwh >= requested_kwh:
                matching_listing = listing
                break

        if not matching_listing:
            print(f"[Marketplace] No available listing for {requested_kwh} kWh")
            return None

        # Confirm the trade
        trade = Trade(matching_listing, buyer_id, requested_kwh)
        matching_listing.status = "matched"
        self.trades[trade.trade_id] = trade

        print(f"[Marketplace] Trade confirmed: {trade.trade_id} | "
              f"Buyer: {buyer_id} | Seller: {trade.seller_id} | "
              f"Total: ${trade.total_cost}")

        # Publish TradeConfirmedEvent for the Settlement service
        self._publish_trade_confirmed_event(trade)
        return trade

    def _publish_trade_confirmed_event(self, trade: Trade):
        """Publish a TradeConfirmedEvent to the event bus."""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "TradeConfirmedEvent",
            "correlation_id": trade.trade_id,
            "trade_id": trade.trade_id,
            "buyer_id": trade.buyer_id,
            "seller_id": trade.seller_id,
            "amount_due": trade.total_cost,
            "quantity_kwh": trade.quantity_kwh
        }
        self.event_bus.publish("trade_confirmed", event)
        print(f"[Marketplace] Published TradeConfirmedEvent for trade {trade.trade_id}")

    def handle_settlement_failed(self, event: dict):
        """Handle a SettlementFailedEvent — compensating transaction."""
        trade_id = event.get("trade_id")
        if trade_id in self.trades:
            trade = self.trades[trade_id]
            trade.status = "reversed"
            # Reopen the listing
            if trade.listing_id in self.listings:
                self.listings[trade.listing_id].status = "open"
            print(f"[Marketplace] Trade {trade_id} reversed. Listing reopened.")