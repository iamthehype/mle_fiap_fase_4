#!/bin/bash

# Local dev 

#poetry install
#poetry run uvicorn app.main:app --reload

# Docker build and run 

docker build -t fcast-api .
docker run -d \
 --name fcast-api \
 -p 8000:8000 \
 fcast-api