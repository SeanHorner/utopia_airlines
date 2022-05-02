# syntax=docker/dockerfile:1
FROM utopia_backend_fastapi_base_image

MAINTAINER Sean Horner "sean.horner@smoothstack.com"
LABEL project="utopia_airlines"

# Changing working directory to the system user's home repository
WORKDIR /home/utopian
# Copying the necessary files into the application folder
COPY api_microservice api_microservice
COPY boot.sh ./
# Ensuring that the entry_script has execution permissions
RUN chmod +x boot.sh

# Setting the DB_ACCESS_URI and SECRET_KEY environmental variables to their secrets mount
ENV DB_ACCESS_URI /run/secrets/utopia_db_uri
ENV SECRET_KEY /run/secrets/utopia_secret_key

# Ensuring that the system user has the appropriate permissions to run the application
RUN chown -R utopian:utopian ./
# Switching to the system user to run the image
USER utopian

# Exposing port 8000 for Uvicorn->FastAPI interactions
EXPOSE 8000

# Setting the entry_script as the images entrypoint
ENTRYPOINT ["./boot.sh"]