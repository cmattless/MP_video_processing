# Use a Python base image
FROM python:3.10-slim

# Install required system libraries
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libegl1-mesa \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    && apt-get clean

RUN echo "Checking Python version"
RUN command -v python3



# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Set default command
CMD ["python", "main.py"]
