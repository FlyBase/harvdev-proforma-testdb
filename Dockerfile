FROM postgres

RUN apt-get update && apt-get install -y software-properties-common python3-pip

ADD . .

RUN pip3 install -r requirements.txt