#!/bin/bash

# stop ElasticSearch servic
echo "Stopping ElasticSearch..."
pkill -f elasticsearch

echo "Waiting 10secs to validate..."
sleep 10

echo "Validate if it is stopped..."
curl -X GET "localhost:9200/?pretty"

if [ $? -eq 0 ]; then
   echo "ElasticSearch is still running..."
else
   echo "ElasticSearch is stopped!"
fi
