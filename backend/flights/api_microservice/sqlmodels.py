from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship


# ------------------------------------------------
#                   Airplane
# ------------------------------------------------


class AirplaneBase(SQLModel):
    type_id: int = Field(nullable=False, foreign_key="airplane_type.id")

    plane_type: "AirplaneType" = Relationship(back_populates="planes_with_type")
    on_flights: List["Flight"] = Relationship(back_populates="airplane")


class Airplane(AirplaneBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class AirplaneCreate(AirplaneBase):
    pass


class AirplaneRead(AirplaneBase):
    id: int


class AirplaneUpdate(SQLModel):
    type_id: Optional[int] = None


# ------------------------------------------------
#                 Airplane Type
# ------------------------------------------------


class AirplaneTypeBase(SQLModel):
    max_capacity: int = Field(nullable=False)

    planes_with_type: List[Airplane] = Relationship(back_populates="plane_type")


class AirplaneType(AirplaneTypeBase, table=True):
    __tablename__ = "airplane_type"
    id: Optional[int] = Field(default=None, primary_key=True)


class AirplaneTypeCreate(AirplaneTypeBase):
    pass


class AirplaneTypeRead(AirplaneTypeBase):
    id: int


class AirplaneTypeUpdate(SQLModel):
    max_capacity: Optional[int] = None


# ------------------------------------------------
#                   Airports
# ------------------------------------------------


class Airport(SQLModel, table=True):
    iata_id: str = Field(nullable=False, primary_key=True)
    city: str = Field(nullable=False)
    name: str
    longitude: float = Field(nullable=False)
    latitude: float = Field(nullable=False)
    elevation: int

    # route_origin: List["Route"] = Relationship(back_populates="origin")
    # route_destination: List["Route"] = Relationship(back_populates="destination")


class AirportCreate(Airport):
    pass


class AirportRead(Airport):
    pass


class AirportUpdate(SQLModel):
    iata_id: Optional[str]
    city: Optional[str]
    name: Optional[str]
    longitude: Optional[float]
    latitude: Optional[float]
    elevation: Optional[int]


# ------------------------------------------------
#                      Flight
# ------------------------------------------------


class FlightBase(SQLModel):
    route_id: int = Field(foreign_key="route.id", nullable=False)
    airplane_id: int = Field(foreign_key="airplane.id", nullable=False)
    departure_time: str = Field(nullable=False, default=str(datetime.utcnow()))
    reserved_seats: int = Field(nullable=False, default=0)
    seat_price: float = Field(nullable=False, default=0.00)

    route: "Route" = Relationship(back_populates="flights")
    airplane: "Airplane" = Relationship(back_populates="on_flights")


class Flight(FlightBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FlightCreate(FlightBase):
    pass


class FlightRead(FlightBase):
    id: int


class FlightUpdate(SQLModel):
    route_id: Optional[int] = None
    airplane_id: Optional[int] = None
    departure_time: Optional[datetime] = None
    reserved_seats: Optional[int] = None
    seat_price: Optional[float] = None


# ------------------------------------------------
#                      Route
# ------------------------------------------------


class RouteBase(SQLModel):
    origin_id: str = Field(nullable=False, foreign_key="airport.iata_id")
    destination_id: str = Field(nullable=False, foreign_key="airport.iata_id")
    duration: Optional[float] = Field(nullable=False)

    flights: List[Flight] = Relationship(back_populates="route")
    # origin: Airport = Relationship(back_populates="route_origin")
    # destination: Airport = Relationship(back_populates="route_destination")


class Route(RouteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class RouteCreate(RouteBase):
    pass


class RouteRead(RouteBase):
    id: int


class RouteUpdate(SQLModel):
    origin_id: Optional[str] = None
    destination_id: Optional[str] = None
    duration: Optional[float] = None
