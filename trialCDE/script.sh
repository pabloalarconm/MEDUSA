#!/bin/bash


# sudo python3 uniq.py ${PWD}/data

irb run_me_to_test.rb personal_information
irb run_me_to_test.rb patient_status
irb run_me_to_test.rb care_pathway
irb run_me_to_test.rb diagnosis
irb run_me_to_test.rb disease_history
irb run_me_to_test.rb genetic_diagnosis
irb run_me_to_test.rb phenotyping
irb run_me_to_test.rb undiagnosis
irb run_me_to_test.rb patient_consent
irb run_me_to_test.rb disability

sudo python3 nt2ttl.py ${PWD}/data/triples

sudo chmod -R 777 .