#!/bin/bash

# start elasticsearch service
echo "Starting ElasticSearch service..."
elasticsearch

echo "Waiting 10secs to validate..."
sleep 30

echo "Validate if it is running..."
curl -X GET "localhost:9200/?pretty"

if [ $? -eq 0 ]; then
   echo "ElasticSearch is running!"
else
   echo "ElasticSearch is not running..."
fi
