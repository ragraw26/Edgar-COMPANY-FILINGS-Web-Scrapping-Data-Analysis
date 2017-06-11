
FROM ubuntu:14.04

MAINTAINER Ankit Bhayani <bhayani.a@husky.neu.edu>

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    python-pip --upgrade python-pip

RUN pip install --upgrade pip


# install py3
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # install python 3
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    pkg-config \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

# install additional python packages
RUN pip3 install ipython
#RUN pip install jupyter
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install scikit-learn
RUN pip3 install BeautifulSoup4
RUN pip3 install scipy
#RUN pip install nltk

#install AWS CLI
RUN pip3 install awscli

#install luigiI
RUN pip3 install luigi

# install unzip utility
#RUN apt-get install unzip

# configure console
RUN echo 'alias ll="ls --color=auto -lA"' >> /root/.bashrc \
 && echo '"\e[5~": history-search-backward' >> /root/.inputrc \
 && echo '"\e[6~": history-search-forward' >> /root/.inputrc

# default password: keras
ENV PASSWD='sha1:98b767162d34:8da1bc3c75a0f29145769edc977375a373407824'

# dump package lists
RUN dpkg-query -l > /dpkg-query-l.txt \
 && pip2 freeze > /pip2-freeze.txt \
 && pip3 freeze > /pip3-freeze.txt

# for jupyter
EXPOSE 8888

# Add a notebook profile.
# RUN mkdir -p -m 700 /root/.jupyter/ && \
#    echo "c.NotebookApp.ip = '*'" >> /root/.jupyter/ClassData_Script.py


WORKDIR /src/

RUN mkdir /src/assignment1
RUN mkdir /src/assignment1/Output
#ADD run.sh /usr/local/bin/run.sh
ADD run.sh /src/assignment1 
ADD driver.sh /src/assignment1 
ADD parsingHTML.py /src/assignment1
ADD edgarLogAnalysis.py /src/assignment1
ADD awsS3Upload.sh /src/assignment1
RUN chmod +x /src/assignment1/run.sh
RUN chmod +x /src/assignment1/driver.sh
RUN chmod +x /src/assignment1/awsS3Upload.sh
#CMD ["/usr/local/bin/run.sh"]

#CMD /bin/bash -c 'jupyter notebook --no-browser --ip=* --NotebookApp.password="$PASSWD" "$@"'
