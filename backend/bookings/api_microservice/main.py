# ######################################################################################################################
# ########################################                               ###############################################
# ########################################              Main             ###############################################
# ########################################                               ###############################################
# ######################################################################################################################
from datetime import datetime
import os
from typing import List

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlmodel import Session, SQLModel, create_engine

from .sqlmodels import *

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
    return {"msg": "Bookings microservice is present and ready for action."}


# ------------------------------------------------
#                   Health Check
# ------------------------------------------------


@app.get("/health")
def health_check():
    return {"msg": "Healthy"}


# ------------------------------------------------
#                     Bookings
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/bookings/", response_model=BookingRead)
def create_booking(booking: BookingCreate, db: Session = Depends(get_session)):
    db_booking = get_booking_by_conf(booking.confirmation_code)

    if db_booking:
        raise HTTPException(
            status_code=400,
            detail="A booking with that confirmation code already exists"
        )

    new_booking = Booking.from_orm(booking)

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return booking


# --------------------   Read   ------------------


@app.get("/api/v2/bookings/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: int, db: Session = Depends(get_session)):
    db_booking = db                             \
        .query(Booking)                         \
        .filter(Booking.id == booking_id)       \
        .first()

    if not db_booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return db_booking


@app.get("/api/v2/bookings/conf_code={conf_code}", response_model=BookingRead)
def get_booking_by_conf(conf_code: str, db: Session = Depends(get_session)):
    db_booking = db                                       \
        .query(Booking)                                   \
        .filter(Booking.confirmation_code == conf_code)   \
        .first()

    if not db_booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return db_booking


@app.get("/api/v2/bookings/", response_model=List[BookingRead])
def get_bookings(skip: int = 0,
                 limit: int = Query(default=100, lte=100),
                 db: Session = Depends(get_session)):
    db_bookings = db        \
        .query(Booking)     \
        .offset(skip)       \
        .limit(limit)       \
        .all()

    if not db_bookings:
        raise HTTPException(
            status_code=404,
            detail="No bookings found"
        )

    return db_bookings


@app.get("/api/v2/bookings/active/", response_model=List[BookingRead])
def get_active_bookings(skip: int = 0,
                        limit: int = 100,
                        db: Session = Depends(get_session)):
    active_bookings = db                \
        .query(Booking)                 \
        .filter(Booking.is_active)      \
        .offset(skip)                   \
        .limit(limit)                   \
        .all()

    if not active_bookings:
        raise HTTPException(
            status_code=404,
            detail="No active bookings found"
        )

    return active_bookings


# --------------------  Update  ------------------


@app.patch("/api/v2/bookings/{booking_id}", response_model=BookingRead)
def update_booking(booking_id: int,
                   booking: BookingUpdate,
                   db: Session = Depends(get_session)):
    db_booking = db                          \
        .query(Booking)                      \
        .filter(Booking.id == booking_id)    \
        .first()

    if not db_booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking_data = booking.dict(exclude_unset=True)
    for key, value in booking_data.items():
        setattr(db_booking, key, value)

    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    return db_booking


# --------------------  Delete  ------------------


@app.delete("/api/v2/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_session)):
    db_booking = db                         \
        .query(Booking)                     \
        .filter(Booking.id == booking_id)   \
        .first()

    if not db_booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    db.delete(db_booking)
    db.commit()

    return {"ok": True}


# ------------------------------------------------
#                 Booking Guest
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/booking_guests/", response_model=BookingGuestRead)
def create_booking_guest(guest: BookingGuestCreate, db: Session = Depends(get_session)):
    db_guest = db                                               \
        .query(BookingGuest)                                    \
        .filter(BookingGuest.booking_id == guest.booking_id)    \
        .first()

    if db_guest:
        raise HTTPException(
            status_code=400,
            detail="Booking guest already exists with that booking id"
        )

    new_guest = BookingGuest.from_orm(guest)

    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)

    return guest


# --------------------   Read   ------------------


@app.get("/api/v2/booking_guests/{booking_id}", response_model=BookingGuestRead)
def get_booking_guest(booking_id: int, db: Session = Depends(get_session)):
    db_guest = db                                           \
        .query(BookingGuest)                              \
        .filter(BookingGuest.booking_id == booking_id)    \
        .first()

    if not db_guest:
        raise HTTPException(
            status_code=404,
            detail="Booking guest not found"
        )

    return db_guest


# --------------------  Update  ------------------


@app.patch("/api/v2/booking_guests/{booking_id}", response_model=BookingGuestRead)
def update_booking_guest(booking_id: int,
                         guest: BookingGuestUpdate,
                         db: Session = Depends(get_session)):
    db_guest = db                                           \
        .query(BookingGuest)                              \
        .filter(BookingGuest.booking_id == booking_id)    \
        .first()

    if not db_guest:
        raise HTTPException(
            status_code=404,
            detail="Booking guest not found"
        )

    guest_data = guest.dict(exclude_unset=True)
    for key, value in guest_data:
        setattr(db_guest, key, value)

    db.add(db_guest)
    db.commit()
    db.refresh(db_guest)

    return db_guest


# --------------------  Delete  ------------------


@app.delete("/api/v2/booking_guests/{booking_id}", response_model=BookingGuestRead)
def delete_booking_guest(booking_id: int, db: Session = Depends(get_session)):
    db_guest = db                                           \
        .query(BookingGuest)                              \
        .filter(BookingGuest.booking_id == booking_id)    \
        .first()

    if not db_guest:
        raise HTTPException(
            status_code=404,
            detail="Booking guest not found"
        )

    db.delete(db_guest)
    db.commit()

    return {"ok": True}


# ------------------------------------------------
#                 Booking Payment
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/booking_payments/", response_model=BookingPaymentRead)
def create_booking_payment(payment: BookingPaymentCreate,
                           db: Session = Depends(get_session)):
    db_payment = db                                                     \
        .query(BookingPayment)                                        \
        .filter(BookingPayment.booking_id == payment.booking_id)      \
        .first()

    if db_payment:
        raise HTTPException(
            status_code=400,
            detail="Payment with that booking id already"
        )

    new_payment = BookingPayment.from_orm(payment)

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


# --------------------   Read   ------------------


@app.get("/api/v2/booking_payments/{booking_id}", response_model=BookingPaymentRead)
def get_booking_payment(booking_id: int, db: Session = Depends(get_session)):
    db_payment = db                                                 \
            .query(BookingPayment)                                \
            .filter(BookingPayment.booking_id == booking_id)      \
            .first()

    if not db_payment:
        raise HTTPException(
            status_code=404,
            detail="Booking payment not found"
        )


@app.get("/api/v2/booking_payments/stripe_id={stripe_id}", response_model=BookingPaymentRead)
def get_booking_payment(stripe_id: str, db: Session = Depends(get_session)):
    db_payment = db                                                 \
            .query(BookingPayment)                                \
            .filter(BookingPayment.stripe_id == stripe_id)      \
            .first()

    if not db_payment:
        raise HTTPException(
            status_code=404,
            detail="Booking payment not found"
        )

    return db_payment


@app.get("/api/v2/booking_payments/", response_model=List[BookingPaymentRead])
def get_booking_payments(skip: int = 0,
                         limit: int = Query(default=100, lte=100),
                         db: Session = Depends(get_session)):
    payments = db                   \
        .query(BookingPayment)      \
        .offset(skip)               \
        .limit(limit)               \
        .all()

    if not payments:
        raise HTTPException(
            status_code=404,
            detail="No booking payments found"
        )

    return payments


@app.get("/api/v2/booking_payments/refunded", response_model=List[BookingPaymentRead])
def get_refunded_booking_payments(skip: int = 0,
                                  limit: int = Query(default=100, lte=100),
                                  db: Session = Depends(get_session)):
    refunded_payments = db                      \
        .query(BookingPayment)                  \
        .filter(BookingPayment.refunded)        \
        .offset(skip)                           \
        .limit(limit)                           \
        .all()

    if not refunded_payments:
        raise HTTPException(
            status_code=404,
            detail="No refunded booking payments found"
        )

    return refunded_payments


@app.get("/api/v2/booking_payments/active", response_model=List[BookingPaymentRead])
def get_refunded_booking_payments(skip: int = 0,
                                  limit: int = Query(default=100, lte=100),
                                  db: Session = Depends(get_session)):
    active_payments = db                        \
        .query(BookingPayment)                  \
        .filter(not BookingPayment.refunded)    \
        .offset(skip)                           \
        .limit(limit)                           \
        .all()

    if not active_payments:
        raise HTTPException(
            status_code=404,
            detail="No active booking payments found"
        )

    return active_payments


# --------------------  Update  ------------------


@app.patch("/api/v2/booking_payments/{booking_id}", response_model=BookingPaymentRead)
def update_booking_payment(payment: BookingPaymentUpdate, db: Session = Depends(get_session)):
    db_payment = db                                                         \
            .query(BookingPayment)                                        \
            .filter(BookingPayment.booking_id == payment.booking_id)      \
            .first()

    if not db_payment:
        raise HTTPException(
            status_code=400,
            detail="Booking payment not found"
        )

    payment_data = payment.dict(exclude_unset=True)
    for key, value in payment_data.items():
        setattr(db_payment, key, value)

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


# --------------------  Delete  ------------------


@app.delete("/api/v2/booking_payments/{booking_id}")
def delete_booking_payment(booking_id: int, db: Session = Depends(get_session)):
    db_payment = db                                                 \
            .query(BookingPayment)                                \
            .filter(BookingPayment.booking_id == booking_id)      \
            .first()

    if not db_payment:
        raise HTTPException(
            status_code=400,
            detail="Booking payment not found"
        )

    db.delete(db_payment)
    db.commit()

    return {"ok": True}


# ------------------------------------------------
#                  Passenger
# ------------------------------------------------

# --------------------  Create  ------------------


@app.post("/api/v2/passengers/", response_model=PassengerRead)
def create_passenger(passenger: Passenger, db: Session = Depends(get_session)):
    db_passenger = db \
        .query(Passenger) \
        .filter(Passenger.booking_id == passenger.booking_id) \
        .first()

    if db_passenger:
        raise HTTPException(
            status_code=400,
            detail="Passenger with that booking id already exists"
        )

    new_passenger = Passenger.from_orm(passenger)

    db.add(new_passenger)
    db.commit()
    db.refresh(new_passenger)

    return passenger


# --------------------   Read   ------------------


@app.get("/api/v2/passengers/{passenger_id}", response_model=PassengerRead)
def get_passenger(passenger_id: int, db: Session = Depends(get_session)):
    db_passenger = db \
        .query(Passenger) \
        .filter(Passenger.id == passenger_id) \
        .first()

    if not db_passenger:
        raise HTTPException(
            status_code=404,
            detail="Passenger not found"
        )

    return db_passenger


@app.get("/api/v2/passengers/", response_model=List[PassengerRead])
def get_passengers(skip: int = 0,
                   limit: int = Query(default=100, lte=100),
                   db: Session = Depends(get_session)):
    passengers = db             \
        .query(Passenger)       \
        .offset(skip)           \
        .limit(limit)           \
        .all()

    if not passengers:
        raise HTTPException(
            status_code=404,
            detail="No passengers found"
        )

    return passengers


@app.get("/api/v2/passengers/booking_id={booking_id}", response_model=List[PassengerRead])
def get_passengers_by_family(booking_id: int,
                             skip: int = 0,
                             limit: int = Query(default=100, lte=100),
                             db: Session = Depends(get_session)):
    passengers = db                                         \
        .query(Passenger)                                   \
        .filter(Passenger.booking_id == booking_id)         \
        .offset(skip)                                       \
        .limit(limit)                                       \
        .all()

    if not passengers:
        raise HTTPException(
            status_code=404,
            detail="No passengers found"
        )

    return passengers


@app.get("/api/v2/passengers/family={family_name}", response_model=List[PassengerRead])
def get_passengers_by_family(family_name: str,
                             skip: int = 0,
                             limit: int = Query(default=100, lte=100),
                             db: Session = Depends(get_session)):
    family = db                                         \
        .query(Passenger)                               \
        .filter(Passenger.family_name == family_name)   \
        .offset(skip)                                   \
        .limit(limit)                                   \
        .all()

    if not family:
        raise HTTPException(
            status_code=404,
            detail="No passengers found"
        )

    return family


@app.get("/api/v2/passengers/family={family_name}", response_model=List[PassengerRead])
def get_passengers_by_dob(dob: datetime.date,
                          skip: int = 0,
                          limit: int = Query(default=100, lte=100),
                          db: Session = Depends(get_session)):
    passengers = db                     \
        .query(Passenger)               \
        .filter(Passenger.dob == dob)   \
        .offset(skip)                   \
        .limit(limit)                   \
        .all()

    if not passengers:
        raise HTTPException(
            status_code=404,
            detail="No passengers found"
        )

    return passengers


# --------------------  Update  ------------------


@app.get("/api/v2/passengers/{passenger_id}", response_model=PassengerRead)
def update_passenger(passenger_id: int,
                     passenger: PassengerUpdate,
                     db: Session = Depends(get_session)):
    db_passenger = db                           \
        .query(Passenger)                       \
        .filter(Passenger.id == passenger_id)   \
        .first()

    if not db_passenger:
        raise HTTPException(
            status_code=404,
            detail="Passenger not found"
        )

    passenger_data = passenger.dict(exclude_unset=True)
    for key, value in passenger_data:
        setattr(db_passenger,  key, value)

    db.add(db_passenger)
    db.commit()
    db.refresh(db_passenger)

    return db_passenger


# --------------------  Delete  ------------------


@app.delete("/api/v2/passengers/{passenger_id}")
def delete_passenger(passenger_id: int, db: Session = Depends(get_session)):
    db_passenger = db \
        .query(Passenger) \
        .filter(Passenger.id == passenger_id) \
        .first()

    if not db_passenger:
        raise HTTPException(
            status_code=404,
            detail="Passenger not found"
        )

    db.delete(db_passenger)
    db.commit()

    return {"ok": True}
