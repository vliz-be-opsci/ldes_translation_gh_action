# Start from a Python image.
FROM python:3.8-slim-buster

# Install Node.js
RUN apt-get update && apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs

# Set the working directory
WORKDIR /src

# Copy the current directory contents into the container at /app
COPY . /src

# the packages to install are from poetry so we need to install it
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

# install all the node dependencies
RUN npm install

# Run app.py when the container launches
CMD ["python", "app.py"]