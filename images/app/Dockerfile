FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt update && apt upgrade -y &&  \
    apt install git adduser -y &&  \
    apt clean && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user that the app will run under.
ARG UID=1001
ARG GID=1001
RUN groupadd --gid ${GID} appuser \
    && adduser --uid ${UID} --gid ${GID} --no-create-home --disabled-password --gecos "" appuser

# Copy the codebase into the container
WORKDIR /ACCS/
COPY . .

# Install dependencies
RUN python -m pip install --no-cache-dir poetry poetry-plugin-export
RUN echo python -m poetry --verion
RUN python -m poetry export --without-hashes --format=requirements.txt -o requirements.txt
RUN python -m pip install -r requirements.txt

# Expose the port that the application listens on
EXPOSE 8000

# Modify owners
RUN chown appuser:appuser -R /ACCS/accs_app
RUN chmod -R 755 /ACCS/accs_app

# Switch workdir
WORKDIR /ACCS/accs_app/

# Switch to the non-privileged user to run the application
USER appuser

# Start app
CMD ["./setup.sh"]