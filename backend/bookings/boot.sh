#!/bin/bash
set -e

echo ""
echo "Beginning SECRET_KEY environmental variable loading..."
# First check if the env var exists at all, if not set to default.
if [ ! -e "$SECRET_KEY" ]; then
  echo " ├─ No SECRET_KEY env var found, falling back to default (i.e. insecure) value..."
  SECRET_KEY="ThisIsNotAVerySafeSecretKeyString"
  echo " ├─ SECRET_KEY set to default value..."
fi
# Then check if the SECRET_FILE env var points to a readable file, in which case read it in as the variable value.
if [ -r "$SECRET_KEY" ]; then
  echo " ├─ SECRET_KEY env var was found set to a file, now reading..."
  SECRET_KEY="$(cat "$SECRET_KEY")"
  echo " ├─ file contents read into SECRET_KEY variable..."
fi
# Next (whether file or not) check if the env var is empty, if so set to default value.
if [ -z "$SECRET_KEY" ]; then
  echo " ├─ SECRET_KEY env var was set to an empty string, falling back to default (i.e. insecure) value..."
  SECRET_KEY="ThisIsNotAVerySafeSecretKeyString"
  echo " ├─ SECRET_KEY set to default value..."
fi
# Finally export the value
export SECRET_KEY="$SECRET_KEY"
echo " └─ SECRET_KEY value exported."
echo ""

echo ""
echo "Beginning DB_ACCESS_URI environmental variable loading..."
# First check if the env var exists at all, if not set to default.
if [ ! -e "$DB_ACCESS_URI" ]; then
  echo " ├─ No DB_ACCESS_URI env var found, falling back to default (i.e. localhost:6603) value..."
  DB_ACCESS_URI="sqlite:///./sql_app.db"
  echo " ├─ DB_ACCESS_URI set to default value..."
fi
# Then check if the SECRET_FILE env var points to a readable file, in which case read it in as the variable value.
if [ -r "$DB_ACCESS_URI" ]; then
  echo " ├─ DB_ACCESS_URI env var was found set to a file, now reading..."
  DB_ACCESS_URI="$(cat "$DB_ACCESS_URI")"
  echo " ├─ file contents read into DB_ACCESS_URI variable..."
fi
# Next check if the env var is empty, if so set to default value.
if [ -z "$DB_ACCESS_URI" ]; then
  echo " ├─ DB_ACCESS_URI env var was set to an empty string, falling back to default (i.e. localhost:6603) value..."
  DB_ACCESS_URI="sqlite:///./sql_app.db"
  echo " ├─ DB_ACCESS_URI set to default value..."
fi
# Finally export the value
export DB_ACCESS_URI="$DB_ACCESS_URI"
echo " └─ DB_ACCESS_URI value exported."
echo ""

exec uvicorn api_microservice.main:app