# Use a Python base image
FROM python:3.10-slim

# Install required system libraries
RUN apt-get update && apt-get install -y \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5network5 \
    libqt5core5a \
    libglu1-mesa \
    libxrender1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    xvfb

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/src

CMD ["python", "-m", "main"]
