# Use the NVIDIA CUDA base image
FROM python:3.10-slim-bullseye

# Install dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential \
  && pip install --no-cache-dir --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Clone the repository and build the project

# Copy requirements and install Python dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

# Copy the application code
COPY . /app

# Set the default command
CMD ["python3", "consumer.py"]