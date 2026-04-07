from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Enum, JSON, BigInteger, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
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

class Amenity(Base):
    __tablename__ = 'amenities'

    # 1. Strings with exact lengths
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(AmenityType), nullable=False)
    floor = Column(Integer, nullable=False)
    
    # 2. Coordinates
    location_x = Column(Float, nullable=False)
    location_y = Column(Float, nullable=False)
    
    # 3. Enums (Using server_default to match DB defaults)
    status = Column(Enum(AmenityStatus), nullable=False, server_default='UNKNOWN')
    crowd_level = Column(Enum(CrowdLevel), nullable=False, server_default='UNKNOWN')
    
    # 4. Replaced estimated_walk_minutes with avg_usage_minutes
    avg_usage_minutes = Column(Integer, nullable=False, default=6)
    
    # 5. Booleans (TinyInt in MySQL) - all marked NOT NULL
    is_wheelchair_accessible = Column(Boolean, nullable=False, default=False)
    is_step_free_route = Column(Boolean, nullable=False, default=False)
    is_family_restroom = Column(Boolean, nullable=False, default=False)
    is_gender_neutral = Column(Boolean, nullable=False, default=False)
    
    confidence_score = Column(Float, nullable=False, default=0.0)
    
    # 6. String(100) and NOT NULL
    gate_proximity = Column(String(100), nullable=False)
    
    # 7. Renamed from data_freshness_timestamp
    last_updated = Column(BigInteger, nullable=False)

    def __repr__(self):
        return f"<Amenity(name='{self.name}', status='{self.status.value}')>"


class CrowdReading(Base):
    __tablename__ = 'crowd_readings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amenity_id = Column(String(50), ForeignKey('amenities.id'), nullable=False)
    crowd_level = Column(Enum(CrowdLevel), nullable=False)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    amenity = relationship('Amenity')

    def __repr__(self):
        return f"<CrowdReading(amenity_id='{self.amenity_id}', crowd_level='{self.crowd_level.value}')>"


class SimulationScenario(Base):
    __tablename__ = 'simulation_scenarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    # JSON structure: {"overrides": {"amenity_id": {"status": "...", "crowd_level": "..."}}}
    config_json = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<SimulationScenario(name='{self.name}')>"
    