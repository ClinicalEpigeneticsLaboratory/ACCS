FROM janbinkowski96/accs-app:latest
#FROM r-base:4.4.0
#ENV DEBIAN_FRONTEND=noninteractive
#
#RUN apt update && apt upgrade -y
#RUN apt install adduser -y
#RUN apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
#        libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev \
#        wget libbz2-dev libcurl4-openssl-dev libssl-dev libxml2-dev -y
#
## Create a non-privileged user that the app will run under.
## See https://docs.docker.com/go/dockerfile-user-best-practices/
#ARG UID=10001
#RUN adduser \
#    --no-create-home \
#    --disabled-password \
#    --gecos "" \
#    --home "/nonexistent" \
#    --shell "/sbin/nologin" \
#    --uid "${UID}" \
#    appuser
#
## Install Python
#RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
#RUN tar -xvf Python-3.10.0.tgz
#RUN cd Python-3.10.0 && ./configure --enable-optimizations && make -j 4 && make altinstall
#RUN python3.10 -m pip install poetry
#
## Copy the codebase into the container.
#COPY requirements.R poetry.lock pyproject.toml ./
#
## Prepare dir for sesame cache
#ENV EXPERIMENT_HUB_CACHE="/usr/local/cache/.ExperimentHub"
#RUN mkdir -p $EXPERIMENT_HUB_CACHE
#
## Install R components
#RUN Rscript requirements.R
#
## Install dependencies
#RUN python3.10 -m poetry export --without-hashes --format=requirements.txt > requirements.txt
#RUN python3.10 -m pip install -r requirements.txt
#
#WORKDIR app/
#COPY accs_app/ .
#
## Expose the port that the application listens on.
#EXPOSE 8000
#
## Switch to the non-privileged user to run the application.
#RUN chown appuser:appuser -R ./
#RUN chmod -R 755 ./
#
#RUN chown appuser:appuser -R $EXPERIMENT_HUB_CACHE
#RUN chmod -R 755 $EXPERIMENT_HUB_CACHE
#
#USER appuser
#
## Run the application.
CMD ["sh", "start_app.sh"]
