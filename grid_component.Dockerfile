# Copyright 2025 Tampere University
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Hamza Rizvi <hamza.rizvi@tuni.fi>

# define the version of Python here
FROM python:3.10.12
LABEL org.opencontainers.image.source https://github.com/secha-project/ev-v2g-simulation-components
LABEL org.opencontainers.image.description "Docker image for the v2g grid component for the SimCES platform."

# create the required directories inside the Docker image
RUN mkdir -p /grid_component
RUN mkdir -p /init
RUN mkdir -p /logs
RUN mkdir -p /simulation-tools
RUN mkdir -p /messages

# install the python libraries inside the Docker image
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# copy the required directories with their content to the Docker image
COPY grid_component/ /grid_component/
COPY messages/ /messages/
COPY init/ /init/
COPY simulation-tools/ /simulation-tools/

# set the working directory inside the Docker image
WORKDIR /

# start command that is run when a Docker container using the image is started

CMD [ "python3", "-u", "-m", "grid_component.grid_component" ]
