# Use the NVIDIA CUDA base image
FROM nvidia/cuda:12.6.3-devel-ubuntu20.04

# Install dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential git libffi-dev python3-minimal python3-pip \
  && pip install --no-cache-dir --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Clone the repository and build the project
RUN git clone --branch Cudapython --single-branch https://github.com/thearpankumar/Encrypt5_SecurityProtocols.git \
    && cd Encrypt5_SecurityProtocols \
    && make

# Copy requirements and install Python dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

# Copy the application code
COPY . /app

# Set the default command
CMD ["python3", "consumer.py"]