#!/bin/bash

# ElasticSearch installation

# import PGP key
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

# install apt repo
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list

# install elasticsearch
sudo apt-get update && sudo apt-get install elasticsearch
