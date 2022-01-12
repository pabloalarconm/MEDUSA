#!/bin/bash

# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" # No need it normally
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" # sometimes linuxbrew doesnt recognize pipenv


pipenv run gen-owl /home/pablo/Desktop/EJP/MEDUSA/trialLinkML/schemas/new_schemas/CDE2biolink_schema_sex.yaml > /home/pablo/Desktop/EJP/MEDUSA/trialLinkML/schemas/new_schemas/owl_sex.owl
pipenv run gen-owl /home/pablo/Desktop/EJP/MEDUSA/trialLinkML/schemas/new_schemas/CDE2biolink_schema_birthdate.yaml > /home/pablo/Desktop/EJP/MEDUSA/trialLinkML/schemas/new_schemas/owl_birthdate.owl
pipenv run gen-owl /home/pablo/Desktop/EJP/MEDUSA/trialLinkML/schemas/new_schemas/CDE2biolink_schema_lab_measurement.yaml > /home/pablo/Desktop/EJP/MEDUSA/trialLinkML/schemas/new_schemas/owl_lab_measurement.owl
