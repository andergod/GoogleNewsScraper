# Use the official Python base image
FROM python:3.11.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxrandr2 \
    libasound2 \
    libxshmfence1 \
    libgbm1 \
    libvulkan1 \
    xdg-utils \
    x11-apps \
    libappindicator3-1 \
    libxss1 \
    libnss3-dev \
    x11-xserver-utils \
    sudo \
    iproute2

# Download and install the specific version of Google Chrome
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_129.0.6668.100-1_amd64.deb && \
    dpkg -i google-chrome-stable_129.0.6668.100-1_amd64.deb || apt-get install -fy

# Clean up the downloaded .deb file
RUN rm google-chrome-stable_129.0.6668.100-1_amd64.deb

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
EXPOSE 6000

# Set the default command to run your application
CMD ["python", "/app/test.py"]

