FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for faster build)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (minimal for faster build)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0 sqlalchemy==2.0.23 python-multipart==0.0.6 python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 python-decouple==3.8 pydantic==2.5.0 email-validator==2.1.0 PyPDF2==3.0.1 requests==2.31.0 aiofiles==23.2.1

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Command to run the application using lightweight startup
CMD ["python", "-c", "import os; import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))"]