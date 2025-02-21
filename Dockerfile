FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

    
# Install Python dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy the local code into the container
COPY ./app /app

# Expose the port that Streamlit runs on
EXPOSE 8501

# Command to start Streamlit. Additional options like --server.enableCORS false ensure cross-origin requests work.
CMD ["streamlit", "run", "main.py", "--server.enableCORS", "false"]