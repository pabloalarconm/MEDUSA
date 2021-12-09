#!/bin/bash

sudo python3 -m rdfizer -c config.ini
sudo python3 nt2ttl.py ${PWD}/data/graph
sudo chmod -R 777 .