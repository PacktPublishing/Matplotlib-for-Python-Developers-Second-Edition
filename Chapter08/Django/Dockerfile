# The official Python 3.6.5 runtime is used as the base image 
FROM python:3.6.5-slim

# Disable buffering of output streams
ENV PYTHONUNBUFFERED 1

# Create a working directory within the container
RUN mkdir /app
WORKDIR /app

# Copy files and directories in the current directory to the container 
ADD . /app/

# Install Django and other dependencies
RUN pip install -r requirements.txt
