# 
FROM python:3.11

# 
WORKDIR /server

# 
COPY ./requirements.txt /server/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /server/requirements.txt

# Install Ollama
RUN pip install ollama

# 
COPY ./app ./app

EXPOSE 27018

# 
CMD ["fastapi", "run", "app/src/main.py", "--port", "8000"]