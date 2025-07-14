# Use Python base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy rest of the app
COPY . .

# Set environment variables
ENV PORT=8000
EXPOSE 8000

# Run server
CMD ["python", "server.py"]
