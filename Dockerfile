FROM r-base:4.4.1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y
RUN apt install adduser -y
RUN apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
        libfontconfig1-dev libcurl4-openssl-dev libharfbuzz-dev libfribidi-dev \
        libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev \
        libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev \
        wget libbz2-dev libssl-dev libxml2-dev pandoc -y

RUN update-ca-certificates
# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --no-create-home \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install Python
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
RUN tar -xvf Python-3.10.0.tgz
RUN cd Python-3.10.0 && ./configure --enable-optimizations && make -j 4 && make altinstall
RUN python3.10 -m pip install poetry

# Copy the codebase into the container
WORKDIR /ACCS/
COPY . .

# Prepare dir for sesame cache
ENV EXPERIMENT_HUB_CACHE="/usr/local/cache/.ExperimentHub"
RUN mkdir -p $EXPERIMENT_HUB_CACHE

# Install R components
RUN Rscript requirements.R
RUN Rscript sesame_cache.R

# Install dependencies
RUN python3.10 -m poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN python3.10 -m pip install -r requirements.txt

# Download ref data for conumee
WORKDIR /ref_data/
RUN wget https://ftp.ncbi.nlm.nih.gov/geo/series/GSE112nnn/GSE112618/suppl/GSE112618_RAW.tar
RUN tar -xf GSE112618_RAW.tar

# Expose the port that the application listens on
EXPOSE 8000

# Modify owners
RUN chown appuser:appuser -R /ACCS/accs_app
RUN chmod -R 755 /ACCS/accs_app

RUN chown appuser:appuser -R $EXPERIMENT_HUB_CACHE
RUN chmod -R 755 $EXPERIMENT_HUB_CACHE

# Switch workdir
WORKDIR /ACCS/accs_app/

# Switch to the non-privileged user to run the application
USER appuser

# Start celery and prepare django to run app
CMD ["./setup.sh"]