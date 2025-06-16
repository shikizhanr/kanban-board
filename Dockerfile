# Start with an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code into the container at /app
COPY ./backend /app/backend
COPY alembic.ini .
COPY migrations /app/migrations

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for PYTHONPATH to include the app directory
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Command to run the application using uvicorn
# It will look for an app instance in backend.app.main
# Ensure backend/app/main.py has an 'app' instance of FastAPI
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
