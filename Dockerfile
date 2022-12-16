FROM python:latest

# get postgres client to enable app to connect to posgtres DB.
RUN apt-get update -qq && apt-get install postgresql-client -y

# install curl to test API calls from app container
RUN apt-get install curl -y

# set working directory
WORKDIR /ingestor

ENV PYTHONPATH "${PYTHONPATH}:/ingestor"

# copy project files.
COPY . .
RUN pip install -r requirements.txt
