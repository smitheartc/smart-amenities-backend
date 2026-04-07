"""
Admin API routes — manage amenity status, crowd levels, and simulation scenarios.

All write operations (PATCH, DELETE, POST) also update `crowd_readings` where
relevant so there is a full audit trail of changes made via the admin panel.

Zone definitions (match Android SimulationLocation enum):
  East Zone    — amenity IDs containing D5–D18   (e.g. REST_D6, FAM_D18)
  Central Zone — amenity IDs containing D19–D30  (e.g. REST_D24, FAM_D28)
  West Zone    — amenity IDs containing D31–D40  (e.g. REST_D36, REST_D40)
  All Zones    — every amenity in Terminal D
"""

import re
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Amenity, AmenityStatus, CrowdLevel, CrowdReading, SimulationScenario
from app.schemas.schemas import (
    AmenityAdminResponse,
    AmenityOverrideRequest,
    ZoneControlRequest,
    ScenarioApplyRequest,
    ScenarioResponse,
    AdminActionResponse,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ── Zone helper ──────────────────────────────────────────────────────────────

def _gate_number(amenity_id: str) -> int | None:
    """Extract the D-gate number from an amenity ID (e.g. REST_D17 → 17)."""
    match = re.search(r'D(\d+)', amenity_id)
    return int(match.group(1)) if match else None


def _amenities_in_zone(amenities: list[Amenity], zone: str) -> list[Amenity]:
    """Filter amenities to those belonging to the requested zone."""
    if zone == "All Zones":
        return amenities
    for amenity in amenities:
        gate = _gate_number(amenity.id)
        if gate is None:
            continue
    zone_map = {
        "East Zone":    lambda g: 5 <= g <= 18,
        "Central Zone": lambda g: 19 <= g <= 30,
        "West Zone":    lambda g: g >= 31,
    }
    predicate = zone_map.get(zone)
    if predicate is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown zone '{zone}'. Valid values: 'All Zones', 'East Zone', 'Central Zone', 'West Zone'"
        )
    return [a for a in amenities if (g := _gate_number(a.id)) is not None and predicate(g)]


def _log_crowd_reading(db: Session, amenity_id: str, crowd_level: CrowdLevel):
    """Insert a crowd_readings row for audit purposes."""
    db.add(CrowdReading(
        amenity_id=amenity_id,
        crowd_level=crowd_level,
        recorded_at=datetime.utcnow()
    ))


# ── GET /api/admin/amenities ─────────────────────────────────────────────────

@router.get("/amenities", response_model=List[AmenityAdminResponse])
def list_all_amenities(db: Session = Depends(get_db)):
    """
    Returns every amenity in Terminal D regardless of status.
    Used by the admin panel to populate the Amenity Overrides list.
    """
    return db.query(Amenity).order_by(Amenity.id).all()


# ── PATCH /api/admin/amenity/{amenity_id} ────────────────────────────────────

@router.patch("/amenity/{amenity_id}", response_model=AmenityAdminResponse)
def update_amenity(
    amenity_id: str,
    body: AmenityOverrideRequest,
    db: Session = Depends(get_db)
):
    """
    Update the status and/or crowd level of a single amenity.
    Omitted fields are left unchanged.
    Also inserts a crowd_readings row when crowd_level changes.
    """
    amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
    if not amenity:
        raise HTTPException(status_code=404, detail=f"Amenity '{amenity_id}' not found")

    if body.status is not None:
        amenity.status = body.status

    if body.crowd_level is not None and body.crowd_level != amenity.crowd_level:
        amenity.crowd_level = body.crowd_level
        _log_crowd_reading(db, amenity_id, body.crowd_level)

    amenity.last_updated = int(datetime.utcnow().timestamp() * 1000)
    db.commit()
    db.refresh(amenity)
    return amenity


# ── DELETE /api/admin/amenity/{amenity_id}/override ──────────────────────────

@router.delete("/amenity/{amenity_id}/override", response_model=AmenityAdminResponse)
def reset_amenity(amenity_id: str, db: Session = Depends(get_db)):
    """
    Reset a single amenity to its neutral state:
      status     → OPEN
      crowd_level → UNKNOWN

    This is what the admin panel's "Reset" button calls.
    """
    amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
    if not amenity:
        raise HTTPException(status_code=404, detail=f"Amenity '{amenity_id}' not found")

    amenity.status = AmenityStatus.OPEN
    amenity.crowd_level = CrowdLevel.UNKNOWN
    amenity.last_updated = int(datetime.utcnow().timestamp() * 1000)
    db.commit()
    db.refresh(amenity)
    return amenity


# ── PATCH /api/admin/zone ────────────────────────────────────────────────────

@router.patch("/zone", response_model=AdminActionResponse)
def update_zone(body: ZoneControlRequest, db: Session = Depends(get_db)):
    """
    Bulk-update all amenities in a zone.

    - crowd_level       → sets crowd level on every amenity in the zone
    - avg_usage_minutes → updates average usage time for every amenity in the zone
    - is_open           → sets status to OPEN (true) or CLOSED (false) for every amenity

    Omitted fields are left unchanged. Crowd level changes are logged to crowd_readings.
    """
    all_amenities = db.query(Amenity).all()
    zone_amenities = _amenities_in_zone(all_amenities, body.zone)

    if not zone_amenities:
        raise HTTPException(
            status_code=404,
            detail=f"No amenities found in zone '{body.zone}'"
        )

    now_ms = int(datetime.utcnow().timestamp() * 1000)
    updated = 0

    for amenity in zone_amenities:
        changed = False

        if body.is_open is not None:
            new_status = AmenityStatus.OPEN if body.is_open else AmenityStatus.CLOSED
            if amenity.status != new_status:
                amenity.status = new_status
                changed = True

        if body.crowd_level is not None and body.crowd_level != amenity.crowd_level:
            amenity.crowd_level = body.crowd_level
            _log_crowd_reading(db, amenity.id, body.crowd_level)
            changed = True

        if body.avg_usage_minutes is not None and body.avg_usage_minutes != amenity.avg_usage_minutes:
            amenity.avg_usage_minutes = body.avg_usage_minutes
            changed = True

        if changed:
            amenity.last_updated = now_ms
            updated += 1

    db.commit()
    return AdminActionResponse(
        success=True,
        message=f"Updated {updated} amenity/amenities in '{body.zone}'",
        updated_count=updated
    )


# ── GET /api/admin/scenarios ─────────────────────────────────────────────────

@router.get("/scenarios", response_model=List[ScenarioResponse])
def list_scenarios(db: Session = Depends(get_db)):
    """
    Returns all simulation scenarios stored in the DB.
    Used by the admin panel's Preset Scenarios block.
    """
    return db.query(SimulationScenario).order_by(SimulationScenario.id).all()


# ── POST /api/admin/scenario/apply ───────────────────────────────────────────

@router.post("/scenario/apply", response_model=AdminActionResponse)
def apply_scenario(body: ScenarioApplyRequest, db: Session = Depends(get_db)):
    """
    Apply a simulation scenario by ID.

    Reads the scenario's config_json and applies each override to the
    corresponding amenity. Unmentioned amenities are left untouched.

    config_json format:
      {
        "overrides": {
          "REST_D22": {"status": "CLOSED"},
          "LAC_D22":  {"crowd_level": "LONG"}
        }
      }
    """
    scenario = db.query(SimulationScenario).filter(SimulationScenario.id == body.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {body.scenario_id} not found")

    overrides: dict = scenario.config_json.get("overrides", {})
    if not overrides:
        return AdminActionResponse(
            success=True,
            message=f"Scenario '{scenario.name}' has no overrides defined",
            updated_count=0
        )

    now_ms = int(datetime.utcnow().timestamp() * 1000)
    updated = 0

    for amenity_id, changes in overrides.items():
        amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
        if not amenity:
            # Scenario references an amenity not in DB — skip silently
            continue

        if "status" in changes:
            try:
                amenity.status = AmenityStatus(changes["status"])
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status '{changes['status']}' in scenario config for '{amenity_id}'"
                )

        if "crowd_level" in changes:
            try:
                new_crowd = CrowdLevel(changes["crowd_level"])
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid crowd_level '{changes['crowd_level']}' in scenario config for '{amenity_id}'"
                )
            if new_crowd != amenity.crowd_level:
                amenity.crowd_level = new_crowd
                _log_crowd_reading(db, amenity_id, new_crowd)

        amenity.last_updated = now_ms
        updated += 1

    db.commit()
    return AdminActionResponse(
        success=True,
        message=f"Applied scenario '{scenario.name}' — {updated} amenity/amenities updated",
        updated_count=updated
    )
