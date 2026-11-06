from typing import Optional
from pydantic import BaseModel, Field, field_validator

class Coordinate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    label: str = Field(default="", max_length=300)

class RouteRequest(BaseModel):
    start: Coordinate
    destination: Coordinate
    travel_mode: str = "car"
    @field_validator("travel_mode")
    @classmethod
    def valid_mode(cls, value):
        if value not in {"car", "bike", "walking"}:
            raise ValueError("travel_mode must be car, bike, or walking")
        return value

class TrafficRequest(BaseModel):
    coordinates: list[list[float]] = Field(min_length=2, max_length=5000)

class IncidentRequest(BaseModel):
    coordinates: list[list[float]] = Field(min_length=2, max_length=5000)

class HazardRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    route_coordinates: list[list[float]] = Field(default_factory=list, max_length=5000)
    precipitation_mm: Optional[float] = Field(default=None, ge=0)
    precipitation_probability: Optional[float] = Field(default=None, ge=0, le=100)
