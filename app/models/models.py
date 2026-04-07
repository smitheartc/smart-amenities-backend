from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Enum, JSON, BigInteger
from sqlalchemy.orm import relationship, declarative_base
import enum
import uuid

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
    
class User(Base):
    __tablename__ = 'users'

    # We use UUIDs for user IDs so they are unguessable
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column('password_hash', String(255), nullable=False)
    