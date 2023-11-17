# Use an official Python runtime as a base image
FROM python:3.8-slim-buster

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit config
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

# Expose port
ENV PORT 8501

# Run streamlit app
CMD ["streamlit", "run", "main.py"]
