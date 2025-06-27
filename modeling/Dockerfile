# Use the official slim Python 3.11 image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to keep the container running for development
CMD ["tail", "-f", "/dev/null"] 