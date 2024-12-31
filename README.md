### Methylation-based Cancer Classifier (MbCC)
The Methylation-based Cancer Classifier (MbCC) is a model registry designed to serve scikit-learn-based machine learning models for omics data, primarily focusing on DNA methylation profiles. 
MbCC provides a user-friendly interface enabling interaction with registered models for data submission, analysis, and secure storage of the generated results.

#### Inference Pipelines
Each sample submitted to MbCC undergoes a standardized, model-specific processing pipeline. The inference pipeline is designed to ensure high data quality, comparability, and accuracy of predictions. It consists of the following steps:

- **Raw Data Processing** -
MbCC expects raw data (currently IDAT files) as input. This step involves pre-processing to prepare data for model consumption. Though computationally intensive, it is crucial for ensuring data interoperability and comparability. Pre-processing operations are model-specific and include normalization, transformation, and imputation steps.

- **Quality Control (QC) Assessment** -
Quality control is performed using anomaly detection models integrated into the pipeline. These models are trained to identify outliers/novelties in the input data, which could impact the primary model's performance. This ensures that potentially problematic samples are detected before processing into next steps.

- **Platform and Sex Inference** - 
This step involves validating the data by comparing inferred characteristics (e.g., platform type and sex) with the metadata expectations. Discrepancies are flagged to ensure input data integrity and to avoid misinterpretation during analysis.

- **Prediction** - 
Once the data has been prepared and assessed, it is passed to the selected model for prediction. The model generates outputs based on the DNA methylation patterns.

- **Copy-Number Variation (CNV) Estimation** - 
MbCC includes a CNV estimation module that leverages IDAT intensities and custom reference samples. This module estimates variations in copy numbers for a set of well-known proto-oncogenes and tumor suppressors, adding an additional layer of actionable insights for downstream analysis.


#### Run app
MbCC's architecture leverages containerization to ensure modularity, scalability, and ease of deployment. The application comprises five key containers, managed using docker-compose:

- **App** - The core component of MbCC is a Django-based web application that handles user interactions, model registration, as well as task orchestration. It acts as the main interface for all operations.

- **Celery** - Celery is employed for task queuing, enabling the asynchronous execution of long-running processes such as raw data processing, quality control, and prediction pipelines.

- **Flower** - Application for monitoring and managing Celery clusters.

- **Redis** - Redis serves as the message broker for Celery, facilitating fast and reliable communication between the task queue and worker processes.

- **Postgres** - The PostgreSQL database is the main storage backend for MbCC, used for maintaining user data, metadata, model registries, and results generated during analysis.

- **Nginx** - Nginx functions as a reverse proxy and web server, managing incoming requests and directing them to the appropriate services while ensuring secure and efficient traffic handling.


**To start MbCC:**

1. create .env file comprising all listed below variables:

```
# DJANGO
DEBUG=
ALLOWED_HOSTS=
CSRF_TRUSTED_ORIGINS=
SECRET_KEY=
DJANGO_SUPERUSER_PASSWORD=
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=

# POSTGRES
DB_HOST=
DB_USER=
DB_PASS=
DB_NAME=
DB_PORT=

# REDIS
REDIS_HOST=
REDIS_PASS=
REDIS_PORT=

# FLOWER
FLOWER_HOST=
FLOWER_UNAUTHENTICATED_API=
FLOWER_PORT=
FLOWER_USER=
FLOWER_PASS=
FLOWER_ENDPOINT=

# SMTP
EMAIL=
EMAIL_PASS=

# SLACK
SLACK_TOKEN=

# TIME
TZ=
```

2. Set up containers

 ```
 # Works only when docker has root-level privileges
 docker compose up --detach
 
 # Otherwise
 sudo docker compose up --detach
 ```

#### Volumes and Networks

**Volumes**:
- postgres_data - This volume is used to persist PostgreSQL database data, ensuring that the database retains its state even if the container is restarted or recreated.

- static_volume - Stores static files for the Django application, such as CSS, JavaScript, and other assets. These files are served by the Nginx container.

- media_volume - Used to store user-uploaded media files, ensuring persistent storage for media assets across container restarts.

**Networks**
- app_network - A bridge network that facilitates communication between the containers (e.g., app, redis, postgres, and nginx). This isolates the application's internal components from external networks, enhancing security and modularity.

#### Nginx
The Nginx server acts as a reverse proxy for the MbCC application, managing secure connections and static file serving. Below are the key aspects of the configuration:

**Nginx Server**
- Upstream App - The upstream block defines the application server, which is the main Django application container.
- HTTP Redirection - Requests made over HTTP are redirected to HTTPS, ensuring all traffic is encrypted.
- HTTPS Configuration - Handles secure HTTPS connections.  SSL/TLS certificates (*.pem and *.key) are used to enable encryption, ensuring data security.
- Strict-Transport-Security (HSTS) is enabled to enforce HTTPS for all subsequent requests.
- client_max_body_size is set to 200M to allow uploading larger files, such as omics data files.

**Nginx Locations**
- Root (/) - Proxies all requests to the upstream app server. 
- Flower (/flower/) - Proxies specific requests to the upstream flower server.
- Static Files (/static/) - Static files, such as CSS and JavaScript.
- Media Files (/media/) - User-uploaded media files.

**Nginx Logging**
- Access logs are written to /var/log/nginx/access.log.
- Error logs are recorded in /var/log/nginx/error.log.

#### Celery
Celery is a key component of the MbCC application, managing asynchronous task execution and enabling efficient handling of computational workloads. 
With Redis, celery supports for autoscaling, task tracking, and logging.

#### Model registry
Each model is a [Nextflow](https://www.nextflow.io/) pipeline designed to load, parse and normalize 
user-uploaded data, and finally, make predictions.

All registered models are listed [here](https://mbcc.pum.edu.pl/models-collection).
