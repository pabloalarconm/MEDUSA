#!/bin/bash


# sudo python3 uniq.py ${PWD}/data

irb run_me_to_test.rb biolink_personal_information
irb run_me_to_test.rb biolink_lab_measurement

sudo python3 nt2ttl.py ${PWD}/data/triples

sudo chmod -R 777 .