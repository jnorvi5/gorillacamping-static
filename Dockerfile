# Use a lightweight base image with Python 3
FROM python:3.10-slim

# Create a directory for your app
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Flask code into the container
COPY . .

# Expose Flask’s port (5000 if using Gunicorn)
EXPOSE 5000

# Start the server with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
