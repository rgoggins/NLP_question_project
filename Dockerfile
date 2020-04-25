# Ubuntu Linux as the base image 
FROM ubuntu:16.04
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install packages, you should modify this based on your program 
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install python3-pip python3-dev &&\ 
    pip3 install spacy && \
#    pip3 install textblob && \
#    pip3 install nltk && \
#    python3 -m spacy download en_core_web_md


# Add the files into container, under QA folder, modify this based on your need 
ADD ask /QA
ADD answer /QA
#ADD answer.py /QA
#ADD ask.py /QA
#ADD tokenizer.py /QA

WORKDIR /QA

# Change the permissions of programs, you may add other command if needed 
CMD ["chmod 777 ask"]
CMD ["chmod 777 answer"]

ENTRYPOINT ["/bin/bash", "-c"]
