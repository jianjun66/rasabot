FROM ubuntu:14.04

COPY . "/app"

WORKDIR "/app"


# use docker-compose to run mongod
#RUN  \
#    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10 && \
#    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/mongodb.list && \
#    apt-get update && \
#	apt-get install -y mongodb-org 

# install python3 and pip3
RUN  \
    apt-get update && \
    apt-get install -y curl &&\
	apt-get install -y python3-pip 


RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py
    
RUN pip3 install --upgrade pip



# Install TensorFlow CPU version.
# with --ignore-installed to fix the "It is a distutils installed project" error
RUN pip install --ignore-installed -r requirements.txt

EXPOSE 8000

CMD ["./run_bot.sh"]
