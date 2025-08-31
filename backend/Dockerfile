FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including build tools for spaCy
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model after spaCy is installed
# Use a more robust approach that won't fail the build
RUN python -c "import spacy; spacy.cli.download('en_core_web_sm')" || \
    python -m spacy download en_core_web_sm || \
    echo "Warning: Could not download spaCy model during build"

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Command to run the application using our startup script
CMD ["python", "startup.py"]