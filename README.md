# microdata-metadata-service
Metadata service for microdata.no.

## Contribute

### Set up
To work on this repository you need to install [poetry](https://python-poetry.org/docs/):
```
# macOS / linux / BashOnWindows
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# Windows powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```
Then install the virtual environment from the root directory:
```
poetry install
```


### Running tests
Open terminal and go to root directory of the project and run:
````
poetry run pytest --cov=metadata_service/
````


### REST API documentation
OpenAPI 3.0 specification file `/static/openapi.json` and ReDoc UI are used to display the REST API documentation.
ReDoc UI is available at `/docs` endpoint.


### Running without Docker
You should add the appropriate environmental variables to your local system:
```sh
export DATASTORE_ROOT_DIR=/datastore
```

Open terminal and go to root directory of the project and run:
````
poetry run gunicorn metadata_service.app:app
````

### Build and run Docker image
````
docker build --tag metadata-service:local-latest .
docker run --publish 8080:8080 \
--rm \
--env DATASTORE_ROOT_DIR=/datastore \
-v /path/to/datastore:/datastore metadata-service:local-latest
````