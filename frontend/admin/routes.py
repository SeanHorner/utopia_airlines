import os
from functools import wraps
from forms import *
from networking import *

import jwt
import requests
from flask import render_template, request, redirect, url_for, make_response, jsonify
from app import app


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        elif 'token' in request.args:
            token = request.args.get('token')
        else:
            return redirect(url_for('/login'))

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            db_user = jsonify(requests.get(f"{USERS_API}/users/{data['user_id']}"))
            identity = db_user.username
        except Exception as e:
            response_obj = {
                'status': 'fail',
                'message': e
            }
            return make_response(jsonify({response_obj})), 403

        return f(*args, **kwargs)
    return decorated


@app.route('/about')
def hello():
    return render_template('about.html', title='About Page')


@app.route('/')
@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title="Sign In", form=form)


@app.route('/register')
def register():
    form = LoginRegistrationForm()
    return render_template('register.html', title='Register', form=form)


@app.route('/airport')
def airport():
    try:
        airports = requests.get(f"{FLIGHTS_API}/airport/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        airports = [
            {
                'iata_id': 'CLE',
                'city': 'Cleveland, OH',
                'name': 'Cleveland Hopkins International Airport',
                'longitude': 41.4117012024,
                'latitude': -81.8498001099,
                'elevation': 791
            },
            {
                'iata_id': 'JFK',
                'city': 'New York, NY',
                'name': 'John F Kennedy International Airport',
                'longitude': 40.639801,
                'latitude': -73.7789,
                'elevation': 13
            }
        ]
    form1 = AirportRegistrationForm()
    form2 = AirportDeletionForm()
    return render_template('airport.html', title="Airport Management", form1=form1, form2=form2, airports=airports)


@app.route('/airplane')
def airplane():
    try:
        airplanes = requests.get(f"{FLIGHTS_API}/airplane/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        airplanes = [
            {
                'id': 1,
                'type_id': 747
            },
            {
                'id': 2,
                'type_id': 858
            },
            {
                'id': 3,
                'type_id': 969
            }
        ]
    form1 = AirplaneRegistrationForm()
    form2 = AirplaneDeletionForm()
    return render_template('airplane.html', title="Airplane Management", form1=form1, form2=form2, airplanes=airplanes)


@app.route('/airplane_type')
def airplane_type():
    try:
        airplane_types = requests.get(f"{FLIGHTS_API}/airplane_type/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        airplane_types = [
            {
                'type_id': 737,
                'max_capacity': 188
            },
            {
                'type_id': 747,
                'max_capacity': 515
            },
            {
                'type_id': 767,
                'max_capacity': 247
            },
            {
                'type_id': 777,
                'max_capacity': 380
            },
            {
                'type_id': 787,
                'max_capacity': 274
            }
        ]
    form1 = AirplaneTypeRegistrationForm()
    form2 = AirplaneTypeDeletionForm()
    return render_template('airplane_type.html', title="Airplane Type Management", form1=form1, form2=form2, airplane_types=airplane_types)


@app.route('/booking')
def booking():
    try:
        bookings = requests.get(f"{BOOKS_API}/booking/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        bookings = []
    form1 = BookingRegistrationForm()
    form2 = BookingDeletionForm()
    return render_template('booking.html', title="Bookings Management", form1=form1, form2=form2, bookings=bookings)


@app.route('/booking_guest')
def booking_guest():
    try:
        booking_guests = requests.get(f"{BOOKS_API}/booking_guest/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        booking_guests = []
    form1 = BookingGuestRegistrationForm()
    form2 = BookingGuestDeletionForm()
    return render_template('booking_guest.html', title="Booking Guest Management", form1=form1, form2=form2, booking_guests=booking_guests)


@app.route('/booking_payment')
def booking_payment():
    try:
        booking_payments = requests.get(f"{BOOKS_API}/booking_payment/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        booking_payments = []
    form1 = BookingPaymentRegistrationForm()
    form2 = BookingPaymentDeletionForm()
    return render_template('booking_payment.html', title="Booking Payment Management", form1=form1, form2=form2, booking_payments=booking_payments)


@app.route('/flight')
def flight():
    try:
        flights = requests.get(f"{FLIGHTS_API}/flight/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        flights = []
    form1 = FlightRegistrationForm()
    form2 = FlightDeletionForm()
    return render_template('flight.html', title="Flight Management", form1=form1, form2=form2, flights=flights)


@app.route('/user')
def user():
    try:
        users = requests.get(f"{USERS_API}/user/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        users = []
    form1 = UserRegistrationForm()
    form2 = UserDeletionForm()
    return render_template('user.html', title="User Management", form1=form1, form2=form2, users=users)


@app.route('/user_role')
def user_role():
    try:
        user_roles = requests.get(f"{FLIGHTS_API}/user_role/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        user_roles = [
            {
                'id': 1,
                'name': 'admin'
            },
            {
                'id': 2,
                'name': 'agent'
            },
            {
                'id': 3,
                'name': 'user'
            }
        ]
    form1 = UserRoleRegistrationForm()
    form2 = UserRoleDeletionForm()
    return render_template('user_role.html', title="User Role Management", form1=form1, form2=form2, user_roles=user_roles)


@app.route('/passenger')
def passenger():
    try:
        passengers = requests.get(f"{BOOKS_API}/passenger/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        passengers = []
    form1 = PassengerRegistrationForm()
    form2 = PassengerDeletionForm()
    return render_template('passenger.html', title="Passenger Management", form1=form1, form2=form2, passengers=passengers)


@app.route('/route')
def route():
    try:
        routes = requests.get(f"{FLIGHTS_API}/route/all")
    except Exception as e:
        print("Error loading values follows:")
        print(e)
        print("Loading dummy data...")
        routes = [
            {
                'id': 1,
                'origin_id': 'CLE',
                'destination_id': 'JFK',
                'duration': 3
            },
            {
                'id': 2,
                'origin_id': 'JFK',
                'destination_id': 'CLE',
                'duration': 2
            }
        ]
    form1 = RouteRegistrationForm()
    form2 = RouteDeletionForm()
    return render_template('route.html', title="Route Management", form1=form1, form2=form2, routes=routes)
