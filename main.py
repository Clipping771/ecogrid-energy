from event_bus.event_bus import EventBus
from services.smart_meter.smart_meter_service import SmartMeterService
from services.marketplace.marketplace_service import MarketplaceService
from services.settlement.financial_settlement_service import FinancialSettlementService


def main():
    print("=" * 60)
    print("EcoGrid Energy — P2P Energy Trading Platform Simulation")
    print("=" * 60)

    # Initialise the shared event bus
    event_bus = EventBus()

    # Initialise all three services
    meter_service = SmartMeterService(event_bus)
    marketplace = MarketplaceService(event_bus)
    settlement = FinancialSettlementService(event_bus)

    # Set up wallets for demo users
    settlement.create_wallet("seller_meter_001", initial_balance=0.0)
    settlement.create_wallet("buyer_household_A", initial_balance=50.0)

    print("\n--- Step 1: Smart Meter Ingests a Reading ---")
    meter_service.ingest_reading(
        device_id="meter_001",
        energy_kwh=5.0,
        reading_type="generation"
    )

    print("\n--- Step 2: Buyer Places a Bid ---")
    marketplace.place_bid(
        buyer_id="buyer_household_A",
        requested_kwh=3.0
    )

    print("\n--- Step 3: Final Wallet Balances ---")
    for user_id, wallet in settlement.wallets.items():
        print(f"  {user_id}: ${wallet.balance}")

    print("\n--- Step 4: Insufficient Funds Test ---")
    marketplace.place_bid(
        buyer_id="buyer_household_A",
        requested_kwh=10.0
    )

    print("\n--- Event Log Summary ---")
    for entry in event_bus.event_log:
        print(f"  Topic: {entry['topic']} | Event: {entry['event']['event_type']}")


if __name__ == "__main__":
    main()