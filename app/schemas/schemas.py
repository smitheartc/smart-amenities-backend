from pydantic import BaseModel, Field
from typing import List, Optional
# Import the Enums you already defined in Models.py
from app.models.models import AmenityType, AmenityStatus, CrowdLevel


# ── Route recommendation (existing) ─────────────────────────────────────────

class RouteRecommendRequest(BaseModel):
    """What Android sends to request route recommendations."""
    user_node: str
    amenity_type: AmenityType
    wheelchair_required: bool = False

class RouteOption(BaseModel):
    """A single recommended route to an amenity."""
    amenity_id: str
    path: List[str]
    walk_seconds: int
    wait_seconds: int
    total_seconds: int
    crowd_level: CrowdLevel
    status: AmenityStatus

class RouteRecommendResponse(BaseModel):
    """Ordered list of route options, sorted by total_seconds."""
    recommendations: List[RouteOption]


# ── Admin — response ─────────────────────────────────────────────────────────

class AmenityAdminResponse(BaseModel):
    """Single amenity record returned by admin endpoints."""
    id: str
    name: str
    type: AmenityType
    floor: int
    status: AmenityStatus
    crowd_level: CrowdLevel
    avg_usage_minutes: int
    is_wheelchair_accessible: bool
    is_step_free_route: bool
    is_family_restroom: bool
    is_gender_neutral: bool
    gate_proximity: str

    class Config:
        from_attributes = True


# ── Admin — requests ─────────────────────────────────────────────────────────

class AmenityOverrideRequest(BaseModel):
    """
    Update the status and/or crowd level of a single amenity.
    Omit a field to leave it unchanged.
    """
    status: Optional[AmenityStatus] = None
    crowd_level: Optional[CrowdLevel] = None

class ZoneControlRequest(BaseModel):
    """
    Bulk-update all amenities in a zone.
    zone values: "All Zones" | "East Zone" | "Central Zone" | "West Zone"
    Omit a field to leave it unchanged across the zone.
    """
    zone: str = Field(..., example="East Zone")
    crowd_level: Optional[CrowdLevel] = None
    avg_usage_minutes: Optional[int] = Field(None, ge=1, le=60)
    is_open: Optional[bool] = None

class ScenarioApplyRequest(BaseModel):
    """Apply a simulation scenario from the DB by its ID."""
    scenario_id: int

class ScenarioResponse(BaseModel):
    """A simulation scenario record."""
    id: int
    name: str
    description: Optional[str]
    config_json: dict

    class Config:
        from_attributes = True

class AdminActionResponse(BaseModel):
    """Generic response for admin write operations."""
    success: bool
    message: str
    updated_count: int = 0