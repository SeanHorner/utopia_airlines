# ######################################################################################################################
# ########################################                               ###############################################
# ########################################              Main             ###############################################
# ########################################                               ###############################################
# ######################################################################################################################
import os
from typing import List

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlmodel import Session, SQLModel, create_engine

from .sqlmodels import (
    Airport, AirportCreate, AirportRead, AirportUpdate,
    Airplane, AirplaneCreate, AirplaneRead, AirplaneUpdate,
    AirplaneType, AirplaneTypeCreate, AirplaneTypeRead, AirplaneTypeUpdate,
    Flight, FlightCreate, FlightRead, FlightUpdate,
    Route, RouteCreate, RouteRead, RouteUpdate
)
from .haversine import Haversine

SQLALCHEMY_DATABASE_URL = os.getenv('DB_ACCESS_URI') or "mysql+pymysql://root:root@127.0.0.1:6603/utopia"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

app = FastAPI()


# ######################################################################################################################
# ########################################                               ###############################################
# ########################################          API Routes           ###############################################
# ########################################                               ###############################################
# ######################################################################################################################


# ------------------------------------------------
#                 Session Creator
# ------------------------------------------------


def get_session():
    with Session(engine) as session:
        yield session


# ------------------------------------------------
#                 Startup DB Creation
# ------------------------------------------------


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# ------------------------------------------------
#                   Roll Call
# ------------------------------------------------


@app.get("/")
def present():
    return {"msg": "Flights microservice is present and ready for action."}


# ------------------------------------------------
#                   Health Check
# ------------------------------------------------


@app.get("/health")
def health_check():
    return {"msg": "Healthy"}


# ------------------------------------------------
#                   Airplane
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/airplanes/", response_model=AirplaneRead)
def create_airplane(
        airplane: AirplaneCreate,
        session: Session = Depends(get_session)):
    db_airplane = Airplane.from_orm(airplane)

    session.add(db_airplane)
    session.commit()
    session.refresh(db_airplane)

    return db_airplane


# --------------------   Read   ------------------


@app.get("/api/v2/airplanes/{airplane_id}", response_model=AirplaneRead)
def get_airplane(
        airplane_id: int,
        session: Session = Depends(get_session)):
    db_airplane = session                           \
        .query(Airplane)                            \
        .filter(Airplane.id == airplane_id)         \
        .first()

    if not db_airplane:
        raise HTTPException(
            status_code=404,
            detail="Airplane not found"
        )

    return db_airplane


@app.get("/api/v2/airplanes/", response_model=List[AirplaneRead])
def get_airplanes(
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    airplanes = session         \
        .query(Airplane)        \
        .offset(skip)           \
        .limit(limit)           \
        .all()

    if not airplanes:
        raise HTTPException(
            status_code=404,
            detail="No airplanes found"
        )

    return airplanes


@app.get("/api/v2/airplanes/type/{type_id}", response_model=List[AirplaneRead])
def get_airplanes_with_type(
        type_id: int,
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    type_airplanes = session                        \
        .query(Airplane)                            \
        .filter(Airplane.type_id == type_id)        \
        .offset(skip)                               \
        .limit(limit)                               \
        .all()

    if not type_airplanes:
        raise HTTPException(
            status_code=404,
            detail="No airplanes found"
        )

    return type_airplanes


# --------------------  Update  ------------------


@app.patch("/api/v2/airplanes/{airplane_id}", response_model=AirplaneRead)
def update_plane(
        airplane_id: int,
        airplane: AirplaneUpdate,
        session: Session = Depends(get_session)):
    db_airplane = session                              \
        .query(Airplane)                          \
        .filter(Airplane.id == airplane_id)       \
        .first()

    if not db_airplane:
        raise HTTPException(
            status_code=404,
            detail="Airplane not found"
        )

    airplane_data = airplane.dict(exclude_unset=True)
    for key, value in airplane_data.items():
        setattr(db_airplane, key, value)

    session.add(db_airplane)
    session.commit()
    session.refresh(db_airplane)

    return db_airplane


# --------------------  Delete  ------------------


@app.delete("/api/v2/airplanes/{airplane_id}")
def delete_airplane(
        airplane_id: int,
        session: Session = Depends(get_session)):
    db_airplane = session                                \
        .query(Airplane)                          \
        .filter(Airplane.id == airplane_id)       \
        .first()

    if not db_airplane:
        raise HTTPException(
            status_code=404,
            detail="Airplane not found"
        )

    session.delete(db_airplane)
    session.commit()

    return {"ok": True}


# ------------------------------------------------
#                 Airplane Type
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/airplane_types/", response_model=AirplaneTypeRead)
def create_airplane_type(
        plane_type: AirplaneTypeCreate,
        session: Session = Depends(get_session)):
    db_type = session                                                   \
        .query(AirplaneType)                                            \
        .filter(AirplaneType.max_capacity == plane_type.max_capacity)   \
        .first()

    if db_type:
        raise HTTPException(
            status_code=400,
            detail="An airplane type with that capacity already exists"
        )

    new_type = AirplaneType.from_orm(plane_type)

    session.add(new_type)
    session.commit()
    session.refresh(new_type)

    return new_type


# --------------------   Read   ------------------


@app.get("/api/v2/airplane_types/{type_id}", response_model=AirplaneTypeRead)
def get_airplane_type(
        type_id: int,
        session: Session = Depends(get_session)):
    db_type = session                                    \
        .query(AirplaneType)                      \
        .filter(AirplaneType.id == type_id)       \
        .first()

    if not db_type:
        raise HTTPException(
            status_code=404,
            detail="Airplane type not found"
        )

    return db_type


@app.get("/api/v2/airplane_types/capacity/{desired_capacity}", response_model=AirplaneTypeRead)
def get_airplane_type_capacity_gt(
        desired_capacity: int,
        session: Session = Depends(get_session)):
    db_type = session                                             \
        .query(AirplaneType)                                      \
        .filter(AirplaneType.max_capacity >= desired_capacity)    \
        .first()

    if not db_type:
        raise HTTPException(
            status_code=404,
            detail="No suitable airplane type not found"
        )

    return db_type


@app.get("/api/v2/airplane_types/", response_model=List[AirplaneTypeRead])
def get_airplane_types(
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    types = session                 \
        .query(AirplaneType)        \
        .offset(skip)               \
        .limit(limit)               \
        .all()

    if not types:
        raise HTTPException(
            status_code=404,
            detail="No airplane types not found"
        )

    return types


# --------------------  Update  ------------------


@app.patch("/api/v2/airplane_types/{type_id}", response_model=AirplaneTypeRead)
def update_airplane_type(
        type_id: int,
        update_type: AirplaneTypeUpdate,
        session: Session = Depends(get_session)):
    db_type = session                             \
        .query(AirplaneType)                      \
        .filter(AirplaneType.id == type_id)       \
        .first()

    if not db_type:
        raise HTTPException(
            status_code=404,
            detail="Airplane type not found"
        )

    type_data = update_type.dict(exclude_unset=True)
    for key, value in type_data.items():
        setattr(db_type, key, value)

    session.add(db_type)
    session.commit()
    session.refresh(db_type)

    return db_type


# --------------------  Delete  ------------------


@app.delete("/api/v2/airplane_types/{type_id}")
def delete_airplane_type(
        type_id: int,
        session: Session = Depends(get_session)):
    db_type = session                             \
        .query(AirplaneType)                      \
        .filter(AirplaneType.id == type_id)       \
        .first()

    if not db_type:
        raise HTTPException(
            status_code=404,
            detail="Airplane type not found"
        )

    affected_planes = session                       \
        .query(Airplane)                            \
        .filter(Airplane.type_id == type_id)        \
        .all()

    if affected_planes:
        for plane in affected_planes:
            session.delete(plane)

    session.delete(db_type)
    session.commit()

    return {"ok": True}


# ------------------------------------------------
#                   Airports
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/airports/", response_model=AirportRead)
def create_airport(
        airport: AirportCreate,
        session: Session = Depends(get_session)):
    db_airport = session                                   \
        .query(Airport)                               \
        .filter(Airport.iata_id == airport.iata_id)   \
        .first()

    if db_airport:
        raise HTTPException(
            status_code=400,
            detail="Airport with that iata_id already exists"
        )

    new_airport = Airport.from_orm(airport)

    session.add(new_airport)
    session.commit()
    session.refresh(new_airport)

    return new_airport


# --------------------   Read   ------------------


@app.get("/api/v2/airports/{iata_id}", response_model=AirportRead)
def get_airport(
        iata_id: str,
        session: Session = Depends(get_session)):
    db_airport = session                                 \
        .query(Airport)                           \
        .filter(Airport.iata_id == iata_id)       \
        .first()

    if not db_airport:
        raise HTTPException(
            status_code=404,
            detail="Airport not found"
        )

    return db_airport


@app.get("/api/v2/airports/city/{city}", response_model=AirportRead)
def get_airports_by_city(
        city: str,
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    city_airports = session                      \
        .query(Airport)                     \
        .filter(Airport.city == city)       \
        .offset(skip)                       \
        .limit(limit)                       \
        .all()

    if not city_airports:
        raise HTTPException(
            status_code=404,
            detail="No airports found for city"
        )

    return city_airports


@app.get("/api/v2/airports/", response_model=List[AirportRead])
def get_airports(
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    airports = session               \
        .query(Airport)         \
        .offset(skip)           \
        .limit(limit)           \
        .all()

    if not airports:
        raise HTTPException(
            status_code=404,
            detail="No airports found"
        )

    return airports


# --------------------  Update  ------------------


@app.patch("/api/v2/airports/{iata_id}", response_model=AirportRead)
def update_airport(
        iata_id: str,
        airport: AirportUpdate,
        session: Session = Depends(get_session)):
    db_airport = session                               \
        .query(Airport)                           \
        .filter(Airport.iata_id == iata_id)       \
        .first()

    if not db_airport:
        raise HTTPException(
            status_code=404,
            detail="Airport not found"
        )

    airport_data = airport.dict(exclude_unset=True)
    for key, value in airport_data.items():
        setattr(db_airport, key, value)

    session.add(db_airport)
    session.commit()
    session.refresh(db_airport)

    return db_airport


# --------------------  Delete  ------------------


@app.delete("/api/v2/airports/{iata_id}")
def delete_airport(
        iata_id: str,
        session: Session = Depends(get_session)):
    db_airport = session                          \
        .query(Airport)                           \
        .filter(Airport.iata_id == iata_id)       \
        .first()

    if not db_airport:
        raise HTTPException(
            status_code=404,
            detail="Airport not found"
        )

    affected_routes = session                             \
        .query(Route)                                     \
        .filter(Route.origin_id == iata_id or
                Route.destination_id == iata_id)          \
        .all()

    if affected_routes:
        for route in affected_routes:
            session.delete(route)

    session.delete(db_airport)
    session.commit()

    return {"ok": True}


# ------------------------------------------------
#                      Flight
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/flights/", response_model=FlightRead)
def create_flight(
        flight: FlightCreate,
        session: Session = Depends(get_session)):
    db_flight = session                   \
        .query(Flight)                    \
        .filter(Flight == flight)         \
        .first()

    if db_flight:
        raise HTTPException(
            status_code=400,
            detail="Flight already exists"
        )

    new_flight = Flight.from_orm(flight)

    session.add(new_flight)
    session.commit()
    session.refresh(new_flight)

    return new_flight


# --------------------   Read   ------------------


@app.get("/api/v2/flights/{flight_id}", response_model=FlightRead)
def get_flight(
        flight_id: int,
        session: Session = Depends(get_session)):
    db_flight = session                       \
        .query(Flight)                        \
        .filter(Flight.id == flight_id)       \
        .first()

    if not db_flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    return db_flight


@app.get("/api/v2/flights/", response_model=List[FlightRead])
def get_flights_by_route(
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    flights = session                               \
        .query(Flight)                              \
        .offset(skip)                               \
        .limit(limit)                               \
        .all()

    if not flights:
        raise HTTPException(
            status_code=404,
            detail="No flights found"
        )

    return flights


@app.get("/api/v2/flights/route/{route_id}", response_model=List[FlightRead])
def get_flights_by_route(
        route_id: int,
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    flights = session                                    \
        .query(Flight)                              \
        .filter(Flight.route_id == route_id)        \
        .offset(skip)                               \
        .limit(limit)                               \
        .all()

    if not flights:
        raise HTTPException(
            status_code=404,
            detail="No flights found"
        )

    return flights


# --------------------  Update  ------------------


@app.patch("/api/v2/flights/{flight_id}", response_model=FlightRead)
def update_flight(
        flight_id: int,
        flight: FlightUpdate,
        session: Session = Depends(get_session)):
    db_flight = session                              \
        .query(Flight)                        \
        .filter(Flight.id == flight_id)       \
        .first()

    if not db_flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    flight_data = flight.dict(exclude_unset=True)
    for key, value in flight_data.items():
        setattr(db_flight, key, value)

    session.add(db_flight)
    session.commit()
    session.refresh(db_flight)

    return db_flight


# --------------------  Delete  ------------------


@app.delete("/api/v2/flights/{flight_id}")
def delete_flight(
        flight_id: int,
        session: Session = Depends(get_session)):
    db_flight = session                       \
        .query(Flight)                        \
        .filter(Flight.id == flight_id)       \
        .first()

    if not db_flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    session.delete(db_flight)
    session.commit()

    return {"ok": True}


# ------------------------------------------------
#                      Route
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/routes/", response_model=RouteRead)
def create_route(
        route: RouteCreate,
        session: Session = Depends(get_session)):
    db_route = session                                          \
        .query(Route)                                           \
        .filter(Route.origin_id == route.origin_id and
                Route.destination_id == route.destination_id)   \
        .first()

    if db_route:
        raise HTTPException(
            status_code=400,
            detail=f"A route between those airports already exists. [id: {db_route.id}]"
        )

    origin = session                                    \
        .query(Airport)                                 \
        .filter(Airport.iata_id == route.origin_id)     \
        .first()

    destination = session                                   \
        .query(Airport)                                     \
        .filter(Airport.iata_id == route.destination_id)    \
        .first()

    distance = Haversine(
        (origin.longitude, origin.latitude),
        (destination.longitude, destination.latitude)
    ).miles

    duration = distance / 500  # Average flight speed is roughly 500 mph

    new_route = Route(
        origin_id=origin.iata_id,
        destination_id=destination.iata_id,
        duration=duration
    )

    session.add(new_route)
    session.commit()
    session.refresh(new_route)

    return new_route


# --------------------   Read   ------------------


@app.get("/api/v2/routes/{route_id}", response_model=RouteRead)
def get_route(route_id: int, session: Session = Depends(get_session)):
    db_route = session                             \
        .query(Route)                         \
        .filter(Route.id == route_id)         \
        .first()

    if not db_route:
        raise HTTPException(
            status_code=404,
            detail="Route not found"
        )

    return db_route


@app.get("/api/v2/routes/", response_model=List[RouteRead])
def get_routes(
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    routes = session                 \
        .query(Route)           \
        .offset(skip)           \
        .limit(limit)           \
        .all()

    if not routes:
        raise HTTPException(
            status_code=404,
            detail="No routes found"
        )

    return routes


@app.get("/api/v2/routes/origin/{iata_id}", response_model=List[RouteRead])
def get_routes_by_origin(
        iata_id: str,
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    routes = session                                     \
        .query(Route)                               \
        .filter(Route.origin_id == iata_id)         \
        .offset(skip)                               \
        .limit(limit)                               \
        .all()

    if not routes:
        raise HTTPException(
            status_code=404,
            detail="No routes found"
        )

    return routes


@app.get("/api/v2/routes/destination/{iata_id}", response_model=List[RouteRead])
def get_routes_by_destination(
        iata_id: str,
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    routes = session                                     \
        .query(Route)                               \
        .filter(Route.destination_id == iata_id)    \
        .offset(skip)                               \
        .limit(limit)                               \
        .all()

    if not routes:
        raise HTTPException(
            status_code=404,
            detail="No routes found"
        )

    return routes


@app.get("/api/v2/routes/duration/{duration}", response_model=List[RouteRead])
def get_routes_by_duration(
        duration: int,
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
        session: Session = Depends(get_session)):
    routes = session                                 \
        .query(Route)                           \
        .filter(Route.duration == duration)     \
        .offset(skip)                           \
        .limit(limit)                           \
        .all()

    if not routes:
        raise HTTPException(
            status_code=404,
            detail="No routes found"
        )

    return routes


# --------------------  Update  ------------------


@app.patch("/api/v2/routes/{route_id}", response_model=RouteRead)
def update_route(
        route_id: int,
        route: RouteUpdate,
        session: Session = Depends(get_session)):
    db_route = session                        \
        .query(Route)                         \
        .filter(Route.id == route_id)         \
        .first()

    if not db_route:
        raise HTTPException(
            status_code=404,
            detail="Route not found"
        )

    route_data = route.dict(exclude_unset=True)
    for key, value in route_data.items():
        setattr(db_route, key, value)

    session.add(db_route)
    session.commit()
    session.refresh(db_route)

    return db_route


# --------------------  Delete  ------------------


@app.delete("/api/v2/routes/{route_id}")
def delete_route(
        route_id: int,
        session: Session = Depends(get_session)):
    db_route = session                        \
        .query(Route)                         \
        .filter(Route.id == route_id)         \
        .first()

    if not db_route:
        raise HTTPException(
            status_code=404,
            detail="Route not found"
        )

    affected_flights = session                    \
        .query(Flight)                            \
        .filter(Flight.route_id == route_id)      \
        .all()

    for flight in affected_flights:
        session.delete(flight.id)

    session.delete(db_route)
    session.commit()

    return {"ok": True}
