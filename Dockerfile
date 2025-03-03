FROM python:3.8-slim

# Set environment variables (can also be provided by Docker run or compose)
ENV PORT=8501

# Set working directory
WORKDIR /app

# Copy the local code into the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install streamlit \
    langchain \
    langchain_community \
    python-decouple \
    openai \
    unstructured \
    "unstructured[pdf]" \
    tiktoken \
    faiss-cpu \
    google_auth_oauthlib \
    jwt \
    supabase

# Expose the port that Streamlit runs on
EXPOSE $PORT

# Command to start Streamlit. Additional options like --server.enableCORS false ensure cross-origin requests work.
CMD ["streamlit", "run", "front_end/main.py", "--server.port", "$PORT", "--server.enableCORS", "false"]