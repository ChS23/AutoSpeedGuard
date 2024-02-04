FROM python:3.11.7-bullseye

#libgl1-mesa-glx
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set the working directory
WORKDIR /app

# Copy only the dependency files to leverage Docker cache
COPY ./pyproject.toml /app/pyproject.toml

# Install Poetry
RUN pip install poetry

# Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root  --verbose

# Copy the entire application code
COPY ./app /app

# Specify the default command to run on container start
CMD ["poetry", "run", "streamlit", "run", "main.py"]
