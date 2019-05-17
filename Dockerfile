FROM postgres

RUN apt-get update && apt-get install -y software-properties-common python3-pip

ADD add-test_data.py .
ADD schema.sql .
ADD requirements.txt .

RUN pip3 install -r requirements.txt
RUN mkdir -p /docker-entrypoint-initdb.d
ADD docker-entrypoint-initdb.d/1_init.sh /docker-entrypoint-initdb.d/1_init.sh

