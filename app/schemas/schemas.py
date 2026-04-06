from pydantic import BaseModel
from typing import List
# Import the Enums you already defined in Models.py
from app.models.models import AmenityType, AmenityStatus, CrowdLevel 

# --- REQUEST SCHEMA ---
class RouteRecommendRequest(BaseModel):
    """What Android sends to you"""
    user_node: str
    amenity_type: AmenityType
    wheelchair_required: bool = False

# --- RESPONSE SCHEMAS ---
class RouteOption(BaseModel):
    """A single recommended route to an amenity"""
    amenity_id: str
    path: List[str]          # Exact node IDs from GraphConstants.kt
    walk_seconds: int
    wait_seconds: int
    total_seconds: int
    crowd_level: CrowdLevel  # Uses the Enum from Models.py
    status: AmenityStatus    # Uses the Enum from Models.py

class RouteRecommendResponse(BaseModel):
    """What you send back to Android"""
    # An ordered list of options, sorted by total_seconds
    recommendations: List[RouteOption]