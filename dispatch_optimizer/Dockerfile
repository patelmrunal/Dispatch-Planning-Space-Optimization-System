# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install streamlit

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for Streamlit
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true

# Entrypoint to run the Streamlit app
CMD ["streamlit", "run", "dispatch_optimizer/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"] 