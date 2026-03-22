"""
Shipment Tracking API
---------------------
A REST API simulating a supply chain visibility platform.

Run:
    cd shipment-api
    uvicorn main:app --reload

Docs:
    http://localhost:8000/docs
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from models import (
    AddEventRequest,
    CreateShipmentRequest,
    ShipmentEvent,
    ShipmentResponse,
)
from store import ShipmentStore

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Shipment Tracking API",
    description=(
        "A REST API that simulates a supply chain visibility platform. "
        "Create shipments, push carrier status events, and track freight in real time.\n\n"
        "**Authentication:** Pass your API key in the `X-API-Key` header.\n\n"
        "Demo key: `demo-key-p44`"
    ),
    version="1.0.0",
)

store = ShipmentStore()

# ── Auth ──────────────────────────────────────────────────────────────────────

VALID_API_KEYS = {"demo-key-p44", "test-key-001"}
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def require_api_key(key: str = Security(api_key_header)) -> str:
    if key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key. Pass a valid key in the X-API-Key header.",
        )
    return key


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    return {
        "service": "Shipment Tracking API",
        "version": "1.0.0",
        "docs": "/docs",
        "demo_api_key": "demo-key-p44",
    }


@app.get(
    "/shipments",
    response_model=list[ShipmentResponse],
    summary="List all shipments",
    tags=["Shipments"],
)
def list_shipments(_: str = Depends(require_api_key)):
    """
    Return all shipments in the system, including their current status and full event history.
    """
    return store.all()


@app.post(
    "/shipments",
    response_model=ShipmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new shipment",
    tags=["Shipments"],
)
def create_shipment(req: CreateShipmentRequest, _: str = Depends(require_api_key)):
    """
    Create a new shipment. The shipment starts with status **Pending** and no events.

    Once created, use `POST /shipments/{id}/events` to push carrier status updates.
    """
    return store.create(req)


@app.get(
    "/shipments/{shipment_id}",
    response_model=ShipmentResponse,
    summary="Get a shipment",
    tags=["Shipments"],
)
def get_shipment(shipment_id: UUID, _: str = Depends(require_api_key)):
    """
    Return full details for a single shipment, including all status events.
    """
    shipment = store.get(shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found.")
    return shipment


@app.get(
    "/shipments/{shipment_id}/events",
    response_model=list[ShipmentEvent],
    summary="Get event history",
    tags=["Events"],
)
def get_events(shipment_id: UUID, _: str = Depends(require_api_key)):
    """
    Return the full status event history for a shipment, in chronological order.

    Each event represents a carrier check-in: a location, status code, and timestamp.
    """
    shipment = store.get(shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found.")
    return shipment.events


@app.post(
    "/shipments/{shipment_id}/events",
    response_model=ShipmentEvent,
    status_code=status.HTTP_201_CREATED,
    summary="Add a status event",
    tags=["Events"],
)
def add_event(shipment_id: UUID, req: AddEventRequest, _: str = Depends(require_api_key)):
    """
    Push a new carrier status event onto a shipment.

    This simulates what happens when a carrier reports a location update or delivery confirmation.
    The shipment's `current_status` is automatically updated to match.

    **Status values:** Pending · Picked Up · In Transit · Out for Delivery · Delivered · Exception
    """
    event = store.add_event(shipment_id, req)
    if event is None:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found.")
    return event
