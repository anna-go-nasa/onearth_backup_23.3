#!/bin/sh
OE_VERSION=${1:-latest}

# Build the onearth-tile-services image
cp ./docker/tile_services/Dockerfile .
docker build --no-cache -t nasagibs/onearth-tile-services:$OE_VERSION .
rm Dockerfile

# Build the onearth-time-service image
cp ./docker/time_service/Dockerfile .
docker build --no-cache -t nasagibs/onearth-time-service:$OE_VERSION .
rm Dockerfile

# Build the onearth-capabilities image
cp ./docker/capabilities/Dockerfile .
docker build --no-cache -t nasagibs/onearth-capabilities:$OE_VERSION .
rm Dockerfile

# Build the onearth-reproject image
cp ./docker/reproject/Dockerfile .
docker build --no-cache -t nasagibs/onearth-reproject:$OE_VERSION .
rm Dockerfile

# Build the onearth-demo image
cp ./docker/demo/Dockerfile .
docker build --no-cache -t nasagibs/onearth-demo:$OE_VERSION .
rm Dockerfile

# Build the onearth-wms image
cp ./docker/wms_service/Dockerfile .
docker build --no-cache -t nasagibs/onearth-wms:$OE_VERSION .
rm Dockerfile

# Build the onearth-tools image
cp ./docker/tools/Dockerfile .
docker build --no-cache -t nasagibs/onearth-tools:$OE_VERSION .
rm Dockerfile