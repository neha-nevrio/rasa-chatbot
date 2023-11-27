FROM rasa/rasa:3.5.12-full
WORKDIR /app

#COPY actions/requirements.txt ./
#
USER root
#
#RUN python3 -m pip install --upgrade pip
#
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip3 install --verbose -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]