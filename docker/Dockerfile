FROM ubuntu:latest AS build

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 pip

RUN mkdir -p /build
COPY Pipfile makefile pytest.ini requirements-dev.in requirements.in setup.cfg setup.py tox.ini README.md /build/
COPY terminusdb_client /build/terminusdb_client
WORKDIR /build

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pipenv --upgrade
RUN pipenv install --dev --pre
RUN python3 -m pip install -e .

RUN useradd -g 1000 -u 1000 -m user
RUN mkdir /tdb
RUN chown user /tdb
COPY docker/run.sh /bin/run.sh

USER user
WORKDIR /tdb

ENTRYPOINT ["/bin/run.sh"]
