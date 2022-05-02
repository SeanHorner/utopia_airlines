import os

BOOKS_API = os.getenv("BOOKS_API") or "http://bookings:5000/api"
DATAPROD = os.getenv("DATAPROD") or "http://data_prod:5000/api"
FLIGHTS_API = os.getenv("FLIGHTS_API") or "http://flights:5000/api"
SECURITY = os.getenv("SECURITY") or "http://security/5000"
USERS_API = os.getenv("USERS_API") or "http://users:5000/api"
ADMIN_ADDR = os.getenv("ADMIN_ADDR") or "http://admin:5000"
