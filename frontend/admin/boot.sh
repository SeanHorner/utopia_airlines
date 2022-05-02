#!/bin/bash
set -e

echo ""
echo "Beginning SECRET_KEY environmental variable loading..."
# First check if the env var exists at all, if not set to default.
if [ ! -e "$SECRET_KEY" ]; then
  echo " ├─ No SECRET_KEY env var found, falling back to default (i.e. insecure) value..."
  SECRET_KEY="ThisIsNotAVerySafeSecretKeyString"
fi
# Then check if the SECRET_FILE env var points to a file, in which case read it in as the variable value.
if [ -f "$SECRET_KEY" ]; then
  echo " ├─ SECRET_KEY env var was found set to a file, now reading..."
  SECRET_KEY="$(cat "$SECRET_KEY")"
fi
# Next (whether file or not) check if the env var is empty, if so set to default value.
if [ -z "$SECRET_KEY" ]; then
  echo " ├─ SECRET_KEY env var was set to an empty string, falling back to default (i.e. insecure) value..."
  SECRET_KEY="ThisIsNotAVerySafeSecretKeyString"
fi
# Finally export the value
export SECRET_KEY="$SECRET_KEY"
echo " └─ SECRET_KEY value exported."
echo ""

# Export all of the networking shortcuts for the backend
export FLIGHTS_API="http://flights:5000/api"
export BOOKINGS_API="http://bookings:5000/api"
export USERS_API="http://users:5000/api"

echo "Waiting a reasonable time for setup to finish..."
sleep 300

#exec python app.py
exec gunicorn -b localhost:5000 --access-logfile - --error-logfile - -w 4 app:app