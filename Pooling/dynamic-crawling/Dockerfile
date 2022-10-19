# Specifying the Platform and Python version for the Docker Image
# For more information, please refer to https://aka.ms/vscode-docker-python
FROM --platform=linux/amd64 python:3.9-slim-buster

# Set current directory as ENV
ENV PATH=/app:$PATH

# Copying/Adding Important Files and Folder referenced by the crawling code to the working directory
# Naming the working directory as "app"
WORKDIR /app
COPY dynamic_crawl.py ./
COPY webdriver_utils.py ./
COPY XPathUtil.py ./
ADD browsermob-proxy-2.1.4 ./browsermob-proxy-2.1.4

# Installing Python dependencies
RUN python -m pip install easyprocess pandas requests tld pyvirtualdisplay bs4 pillow browsermob-proxy adblockparser selenium domain-utils datetime

# Installing TigerVNC for remote access
RUN apt update
RUN apt install -y tigervnc-standalone-server default-jre wget

# Installing the latest stable version of google chrome (v106) for instrumentation
RUN apt -f install -y
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install ./google-chrome-stable_current_amd64.deb -y

# Download chromedriver for 64-bit linux
RUN apt-get install zip unzip
RUN wget https://chromedriver.storage.googleapis.com/106.0.5249.61/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip