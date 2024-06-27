# Dockerized-Flask-API
General API to handle receiving of large data file chunks via HTTP requests
- Elements within `<>` are values you must fill in

# Requirements
  - Host server with Docker installed
  - Docker Desktop for remote repository of docker image

# Building Dockerized Application onto Remote Server
  Move to the directory with the Dockerfile
  
  Run `docker build -t <image-name> .`
  
  Tag the docker image
  - `docker tag <image-id> <repository-name>:<tag>`
  - repository-name is in the form `<username>/<image-name>`
  
  Push docker image to an online repository
  - `docker login`
  - `docker push <repository-name>:<tag>`
  
  Log into remote server, run the following command to pull from the online repository
  - `docker login`
  - `docker pull <repository-name>:<tag>`

# Running Docker image in a container in detached mode w/ mounted local directory
  To have the Flask application's `/app/uploads` directory mounted to a given file directory on host machine 
  - `docker run -d -v <host-machine-directory>:/app/uploads -p <host-port-number>:<container-port-number> <Docker-image>`

# Miscellaneous configuration for Docker container that you can do
  Setting name to container during the mounting process
  - `docker run -d --name <container-name> -v <host-machine-directory>:/app/uploads -p <host-port-number>:<container-port-number> <Docker-image>`

  Checking the uploads folder of the dockerized flask server:
  - `docker exec -it <Docker-container-ID> ls ./uploads`
  
