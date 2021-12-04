# Dockerized python client

```
DOCKER_USER=terminusdb
DOCKER_IMAGENAME=$DOCKER_USER/terminusdb-python

docker build --pull -t "$DOCKER_IMAGENAME" -f docker/Dockerfile .
docker push "$DOCKER_IMAGENAME"

docker run --rm -it -v $PWD/tdb:/tdb "$DOCKER_IMAGENAME" startproject
# https://cloud.terminusdb.com
# Enter your teamname on TerminusX
# JWT token must be used with environment variable instead 

TERMINUSDB_ACCESS_TOKEN=ey... # Insert terminusX access token here
docker run --rm -it -e TERMINUSDB_ACCESS_TOKEN=$TERMINUSDB_ACCESS_TOKEN -v $PWD/tdb:/tdb "$DOCKER_IMAGENAME" commit
```

You can also use an alias like so (note that tdb will be created automatically in your home directory):
You may also need to make the folder writable to the in-docker user (uid 1000, gid 1000)
```
mkdir $HOME/tdb
TERMINUSDB_ACCESS_TOKEN=ey...
alias terminusdb='docker run --rm -it -e TERMINUSDB_ACCESS_TOKEN=$TERMINUSDB_ACCESS_TOKEN -v $HOME/tdb:/tdb "$DOCKER_IMAGENAME"'
```
