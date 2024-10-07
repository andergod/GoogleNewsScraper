# Use the official Python base image
FROM python:3.12-slim

# Install curl and other dependencies for Poetry and building the app
RUN apt-get update && apt-get install -y curl build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set environment variable to disable virtual environment creation
ENV POETRY_VIRTUALENVS_CREATE=false

# Add Poetry to the system path
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy only the pyproject.toml and poetry.lock first to leverage Docker's caching
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Expose the application port (adjust based on your app’s requirements)
EXPOSE 8000

# Set the default command to run your application
CMD ["python", "-m", "app"]
