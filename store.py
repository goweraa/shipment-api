"""
In-memory shipment store. Pre-loaded with sample shipments for demo purposes.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID, uuid4

from models import (
    AddEventRequest,
    CreateShipmentRequest,
    ShipmentEvent,
    ShipmentResponse,
    ShipmentStatus,
)


class ShipmentStore:
    def __init__(self) -> None:
        self._shipments: dict[UUID, ShipmentResponse] = {}
        self._seed()

    # ── Public API ────────────────────────────────────────────────────────────

    def all(self) -> list[ShipmentResponse]:
        return list(self._shipments.values())

    def get(self, shipment_id: UUID) -> ShipmentResponse | None:
        return self._shipments.get(shipment_id)

    def create(self, req: CreateShipmentRequest) -> ShipmentResponse:
        now = datetime.utcnow()
        shipment = ShipmentResponse(
            shipment_id=uuid4(),
            pro_number=req.pro_number,
            carrier_scac=req.carrier_scac,
            carrier_name=req.carrier_name,
            origin_city=req.origin_city,
            origin_state=req.origin_state,
            destination_city=req.destination_city,
            destination_state=req.destination_state,
            shipper_name=req.shipper_name,
            consignee_name=req.consignee_name,
            current_status=ShipmentStatus.PENDING,
            created_at=now,
            last_updated=now,
            events=[],
        )
        self._shipments[shipment.shipment_id] = shipment
        return shipment

    def add_event(self, shipment_id: UUID, req: AddEventRequest) -> ShipmentEvent | None:
        shipment = self._shipments.get(shipment_id)
        if shipment is None:
            return None

        event = ShipmentEvent(
            event_id=uuid4(),
            status=req.status,
            city=req.city,
            state=req.state,
            note=req.note,
            timestamp=datetime.utcnow(),
        )
        shipment.events.append(event)
        shipment.current_status = req.status
        shipment.last_updated = event.timestamp
        return event

    # ── Seed data ─────────────────────────────────────────────────────────────

    def _seed(self) -> None:
        """Pre-load three realistic sample shipments so the API isn't empty on startup."""

        now = datetime.utcnow()

        # Shipment 1 — Delivered
        s1 = ShipmentResponse(
            shipment_id=uuid4(),
            pro_number="PRO-789001",
            carrier_scac="CRTR",
            carrier_name="Central Freight",
            origin_city="Chicago", origin_state="IL",
            destination_city="Indianapolis", destination_state="IN",
            shipper_name="Acme Manufacturing",
            consignee_name="Beta Distribution",
            current_status=ShipmentStatus.DELIVERED,
            created_at=now - timedelta(days=2),
            last_updated=now - timedelta(hours=3),
            events=[
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.PICKED_UP,
                              city="Chicago", state="IL", note="Driver collected freight",
                              timestamp=now - timedelta(days=2)),
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.IN_TRANSIT,
                              city="Gary", state="IN", note="Arrived at relay terminal",
                              timestamp=now - timedelta(days=1, hours=6)),
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.OUT_FOR_DELIVERY,
                              city="Indianapolis", state="IN", note="On truck for final delivery",
                              timestamp=now - timedelta(hours=5)),
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.DELIVERED,
                              city="Indianapolis", state="IN", note="Signed by J. SMITH",
                              timestamp=now - timedelta(hours=3)),
            ],
        )

        # Shipment 2 — In Transit
        s2 = ShipmentResponse(
            shipment_id=uuid4(),
            pro_number="PRO-789002",
            carrier_scac="ODFL",
            carrier_name="Old Dominion Freight",
            origin_city="Dallas", origin_state="TX",
            destination_city="Atlanta", destination_state="GA",
            shipper_name="TexPro Supplies",
            consignee_name="SouthEast Retail",
            current_status=ShipmentStatus.IN_TRANSIT,
            created_at=now - timedelta(days=1),
            last_updated=now - timedelta(hours=2),
            events=[
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.PICKED_UP,
                              city="Dallas", state="TX", note=None,
                              timestamp=now - timedelta(days=1)),
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.IN_TRANSIT,
                              city="Shreveport", state="LA", note="Passed through hub",
                              timestamp=now - timedelta(hours=2)),
            ],
        )

        # Shipment 3 — Exception
        s3 = ShipmentResponse(
            shipment_id=uuid4(),
            pro_number="PRO-789003",
            carrier_scac="SAIA",
            carrier_name="Saia LTL Freight",
            origin_city="Los Angeles", origin_state="CA",
            destination_city="Phoenix", destination_state="AZ",
            shipper_name="West Coast Goods",
            consignee_name="Desert Distributors",
            current_status=ShipmentStatus.EXCEPTION,
            created_at=now - timedelta(days=3),
            last_updated=now - timedelta(hours=8),
            events=[
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.PICKED_UP,
                              city="Los Angeles", state="CA", note=None,
                              timestamp=now - timedelta(days=3)),
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.IN_TRANSIT,
                              city="San Bernardino", state="CA", note=None,
                              timestamp=now - timedelta(days=2)),
                ShipmentEvent(event_id=uuid4(), status=ShipmentStatus.EXCEPTION,
                              city="Blythe", state="CA",
                              note="Address not found — consignee contact required",
                              timestamp=now - timedelta(hours=8)),
            ],
        )

        for s in [s1, s2, s3]:
            self._shipments[s.shipment_id] = s
