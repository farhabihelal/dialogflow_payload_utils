# Dialogflow Payload Utils

This repo depends on the Dialogflow API which is included in this repo as a submodule. 

Please follow these steps to properly set up the environment-

```bash
# initialize and update dialogflow-api submodule
git submodule update --init

# create python virtual environments and install the required packages. 
python3 -m venv venv

source ./venv/bin/activate

(venv) pip install -U pip
(venv) pip install -r ./requirements.txt

# download spacy language model
(venv) spacy download "en-core-web-sm"

# run the desired tool with supplying proper arguments.
(venv) python src/${TOOL}.py --project_id ${PROJECT_ID} --credential ${AGENT_CREDENTIAL_PATH}

```


