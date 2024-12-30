FROM r-base:4.4.1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y
RUN apt install adduser -y
RUN apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
        libfontconfig1-dev libcurl4-openssl-dev libharfbuzz-dev libfribidi-dev \
        libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev \
        libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev \
        wget libbz2-dev libssl-dev libxml2-dev pandoc openjdk-17-jdk -y && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-privileged user that the app will run under.
# Do not --no-create-home for nextflow
ARG UID=1001
ARG GID=1001
RUN groupadd --gid ${GID} appuser \
    && adduser --uid ${UID} --gid ${GID} --disabled-password --gecos "" appuser

# Install Python
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
RUN tar -xvf Python-3.10.0.tgz
RUN cd Python-3.10.0 && ./configure --enable-optimizations && make -j 4 && make altinstall

# Install Nextflow
RUN wget -qO- https://get.nextflow.io | bash \
    && mv nextflow /usr/local/bin/  \
    && chown appuser:appuser /usr/local/bin/nextflow \
    && chmod +x /usr/local/bin/nextflow

# Copy the codebase into the container
WORKDIR /ACCS/

# Install Python dependencies
COPY poetry.lock pyproject.toml ./
RUN python3.10 -m pip install poetry
RUN python3.10 -m poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN python3.10 -m pip install -r requirements.txt

# Prepare dir for sesame cache
ENV EXPERIMENT_HUB_CACHE="/usr/local/cache/.ExperimentHub"
RUN mkdir -p $EXPERIMENT_HUB_CACHE

# Install R components
COPY requirements.R sesame_cache.R ./
RUN Rscript requirements.R
RUN Rscript sesame_cache.R

# Download ref data for conumee
WORKDIR /ref_data/
RUN wget https://ftp.ncbi.nlm.nih.gov/geo/series/GSE112nnn/GSE112618/suppl/GSE112618_RAW.tar
RUN tar -xf GSE112618_RAW.tar

# Switch workdir and copy codebase
WORKDIR /ACCS/accs_app/
COPY . .

# Modify ownership
RUN chown appuser:appuser -R /ACCS/accs_app
RUN chmod -R 755 /ACCS/accs_app

RUN chown appuser:appuser -R $EXPERIMENT_HUB_CACHE
RUN chmod -R 755 $EXPERIMENT_HUB_CACHE

# Switch to the non-privileged user to run the application
USER appuser

# Run cellery
ENTRYPOINT ["python3.10", "-m", "celery", "--app=accs_app.celery", "worker", "--pool=eventlet", "--autoscale=3,1", "-E"]
