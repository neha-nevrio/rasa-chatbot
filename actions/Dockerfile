FROM rasa/rasa-sdk:3.5.1

COPY actions/requirements.txt requirements.txt
#COPY Store Store
COPY Knowledge Knowledge
COPY .env .env
USER root
RUN python -m pip install --upgrade pip
RUN pip install --verbose -r requirements.txt

