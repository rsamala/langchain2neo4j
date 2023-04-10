# Use the official Python base image with the desired version
FROM python:3.11

# Set the working directory
WORKDIR /app

COPY p* /app

# Install Poetry
RUN pip install poetry==1.4.2

# Install project dependencies using Poetry
RUN poetry install

# Copy the project files into the container
COPY ./src /app

# Expose any necessary ports
EXPOSE 7860

# Start the application
CMD ["poetry", "run", "python", "main.py"]