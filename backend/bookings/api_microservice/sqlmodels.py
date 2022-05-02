from typing import Optional, List
import datetime

from sqlmodel import Field, SQLModel, Relationship


# ------------------------------------------------
#                     Bookings
# ------------------------------------------------


class BookingBase(SQLModel):
    is_active: bool = Field(default=True)
    confirmation_code: str

    payment: "BookingPayment" = Relationship(back_populates="booking")
    guest: Optional["BookingGuest"] = Relationship(back_populates="booking")
    passenger: Optional["Passenger"] = Relationship(back_populates="booking")


class Booking(BookingBase, table=True):
    id: Optional[int] = Field(primary_key=True)


class BookingCreate(BookingBase):
    pass


class BookingRead(BookingBase):
    id: int


class BookingUpdate(SQLModel):
    is_active: Optional[bool] = None
    confirmation_code: Optional[str] = None


# ------------------------------------------------
#                 Booking Guest
# ------------------------------------------------


class BookingGuest(SQLModel, table=True):
    booking_id: Optional[int] = Field(foreign_key="booking.id", primary_key=True)
    contact_email: str = Field(primary_key=True)
    contact_phone: str

    booking: Booking = Relationship(back_populates="guest")


class BookingGuestCreate(BookingGuest):
    pass


class BookingGuestRead(BookingGuest):
    pass


class BookingGuestUpdate(SQLModel):
    booking_id: Optional[int] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


# ------------------------------------------------
#                 Booking Payment
# ------------------------------------------------


class BookingPayment(SQLModel, table=True):
    booking_id: Optional[int] = Field(foreign_key="booking.id", primary_key=True)
    stripe_id: str = Field(primary_key=True)
    refunded: bool = Field(default=False)

    booking: Booking = Relationship(back_populates="payment")


class BookingPaymentCreate(BookingPayment):
    pass


class BookingPaymentRead(BookingPayment):
    pass


class BookingPaymentUpdate(SQLModel):
    booking_id: Optional[int] = None
    stripe_id: Optional[str] = None
    refunded: Optional[bool] = None


# ------------------------------------------------
#                  Passenger
# ------------------------------------------------


class PassengerBase(SQLModel):
    booking_id: int = Field(foreign_key="booking.id")
    given_name: str
    family_name: str
    dob: datetime.date
    gender: str
    address: str

    booking: List[Booking] = Relationship(back_populates="passenger")


class Passenger(PassengerBase, table=True):
    id: Optional[int] = Field(primary_key=True)


class PassengerCreate(PassengerBase):
    pass


class PassengerRead(PassengerBase):
    id: int


class PassengerUpdate(SQLModel):
    booking_id: Optional[int] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    dob: Optional[datetime.date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
