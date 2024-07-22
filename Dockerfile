# Use the official Python image
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /

# Copy the FastAPI app code to the container
COPY . /

# Install any dependencies
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]