#!/bin/bash


# sudo python3 uniq.py ${PWD}/data

irb run_me_to_test.rb personal_information_biolink
irb run_me_to_test.rb lab_measurement_biolink

sudo python3 nt2ttl.py ${PWD}/data/triples

sudo chmod -R 777 .