from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Enum, JSON, BigInteger
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

# --- Enums from Models.kt ---

class AmenityType(enum.Enum):
    RESTROOM = "Restroom"
    FAMILY_RESTROOM = "Family Restroom"
    LACTATION_ROOM = "Lactation Room"
    GENDER_NEUTRAL_RESTROOM = "Gender-Neutral Restroom"
    WATER_FOUNTAIN = "Water Fountain"

class AmenityStatus(enum.Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    OUT_OF_SERVICE = "Out of Service"
    UNKNOWN = "Status Unknown"

class CrowdLevel(enum.Enum):
    EMPTY = "Empty"
    SHORT = "Short Wait"
    MEDIUM = "Medium Wait"
    LONG = "Long Wait"
    UNKNOWN = "Unknown"

    @property
    def wait_estimate_minutes(self) -> int:
        """
        Returns the estimated wait time in minutes associated with the crowd level.
        Matches the waitEstimateMinutes from the Kotlin domain model.
        """
        mapping = {
            self.EMPTY: 0,
            self.SHORT: 0,
            self.MEDIUM: 5,
            self.LONG: 10,
            self.UNKNOWN: 0
        }
        return mapping.get(self, 0)

class DirectionIcon(enum.Enum):
    STRAIGHT = "STRAIGHT"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"
    # ... include others (ELEVATOR_UP, ARRIVE, etc.)

class Amenity(Base):
    __tablename__ = 'amenities'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(AmenityType), nullable=False)
    floor = Column(Integer, nullable=False)
    
    # Normalized map coordinates
    location_x = Column(Float, nullable=False)
    location_y = Column(Float, nullable=False)
    
    status = Column(Enum(AmenityStatus), default=AmenityStatus.UNKNOWN)
    crowd_level = Column(Enum(CrowdLevel), default=CrowdLevel.UNKNOWN)
    
    estimated_walk_minutes = Column(Integer, default=0)
    is_wheelchair_accessible = Column(Boolean, default=False)
    is_step_free_route = Column(Boolean, default=False)
    is_family_restroom = Column(Boolean, default=False)
    is_gender_neutral = Column(Boolean, default=False)
    
    data_freshness_timestamp = Column(BigInteger)  # Unix millis
    confidence_score = Column(Float, default=1.0)
    gate_proximity = Column(String)

    def __repr__(self):
        return f"<Amenity(name='{self.name}', status='{self.status.value}')>"
    
class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amenity_id = Column(String, ForeignKey('amenities.id'))
    total_walk_minutes = Column(Integer)
    total_wait_minutes = Column(Integer)
    is_step_free_route = Column(Boolean)
    computed_at_timestamp = Column(BigInteger)

    # Relationship to steps
    steps = relationship("NavigationStep", back_populates="route", cascade="all, delete-orphan")

class NavigationStep(Base):
    __tablename__ = 'navigation_steps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    step_number = Column(Integer, nullable=False)
    instruction = Column(String, nullable=False)
    direction_icon = Column(Enum(DirectionIcon))
    distance_meters = Column(Float)
    
    # Floor transition stored as JSON or a composite; here we use a simple JSON blob 
    # to mirror the FloorTransition data class without needing another table
    floor_transition = Column(JSON, nullable=True) 

    route = relationship("Route", back_populates="steps")