"""
Data models for the Shipment Tracking API.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ShipmentStatus(str, Enum):
    PENDING       = "Pending"
    PICKED_UP     = "Picked Up"
    IN_TRANSIT    = "In Transit"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERED     = "Delivered"
    EXCEPTION     = "Exception"


class CreateShipmentRequest(BaseModel):
    pro_number:   str = Field(..., example="PRO-123456", description="Carrier's tracking number")
    carrier_scac: str = Field(..., example="FXFE", description="4-letter carrier code (SCAC)")
    carrier_name: str = Field(..., example="FedEx Freight", description="Carrier display name")
    origin_city:       str = Field(..., example="Chicago")
    origin_state:      str = Field(..., example="IL")
    destination_city:  str = Field(..., example="Indianapolis")
    destination_state: str = Field(..., example="IN")
    shipper_name:  str = Field(..., example="Acme Corp")
    consignee_name: str = Field(..., example="Beta Warehouse")


class AddEventRequest(BaseModel):
    status:   ShipmentStatus = Field(..., description="New shipment status")
    city:     str = Field(..., example="Gary")
    state:    str = Field(..., example="IN")
    note:     Optional[str] = Field(None, example="Arrived at sorting facility")


class ShipmentEvent(BaseModel):
    event_id:  UUID
    status:    ShipmentStatus
    city:      str
    state:     str
    note:      Optional[str]
    timestamp: datetime


class ShipmentResponse(BaseModel):
    shipment_id:       UUID
    pro_number:        str
    carrier_scac:      str
    carrier_name:      str
    origin_city:       str
    origin_state:      str
    destination_city:  str
    destination_state: str
    shipper_name:      str
    consignee_name:    str
    current_status:    ShipmentStatus
    created_at:        datetime
    last_updated:      datetime
    events:            list[ShipmentEvent] = []
