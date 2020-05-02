# IR project (shazam)

## How to run

1) Download index from https://drive.google.com/open?id=1mUER-xSxItbWKEfywzuRUDZa8LFZt0qN
2) Create dir for indexes: `mkdir docker/volumes -p`
2) Put index files into docker/volumes (you need to put at least one index file)
3) Build docker container 

```docker build docker/ -t project```

4) Run container 

```docker run --rm -p 8080:8080 -v $(pwd)/docker/volumes/:/usr/src/app/volumes project```

5) Send post request with subsample of audiofile to 127.0.0.1:8080, for example using curl: 

```curl -X POST --data-binary @requests/Again.m4a 127.0.0.1:8080/```

where `requests/Again.m4a` relative path to file

6) Stop container

```docker container stop server1```

## Run multiple servers (Update 02.05.2020)


1) Download index from https://drive.google.com/open?id=1mUER-xSxItbWKEfywzuRUDZa8LFZt0qN

2) Create dirs for indexes of each server. For example: `mkdir docker/volumes/server1 docker/volumes/server2 -p`

3) Put index files into dirs from previous step (you need to put at least one index file). For example you can put first half of files into `docker/volumes/server1` and others into `docker/volumes/server2`

4) Build docker containers

```
docker build docker/ -t project
docker build docker/Dockerfile_reducer -t project_reducer
```

5) Create net for containers

```
docker network create project-net
```

6) Run servers containers

```
docker run --rm --net project-net --name server1 -v $(pwd)/docker/volumes/server1:/usr/src/app/volumes project
docker run --rm --net project-net --name server2 -v $(pwd)/docker/volumes/server2:/usr/src/app/volumes project
```

7) Make config for reducer 

First, we need to find out ip addres of each container. To do it we can run 

```docker inspect server1 | grep IPAddress```

 In may case it return:

 ```
"SecondaryIPAddresses": null,
            "IPAddress": "",
                    "IPAddress": "172.21.0.2",

 ```
This mean that ip of our server is `172.21.0.2`

We need to repeat this action for each server.
At the end we need to put all ip-addresses (with 8080 port) into `docker/volumes/servers.cfg`. My `servers.cfg`:

```
http://172.21.0.3:8080
http://172.21.0.2:8080
```

8) Run reducer container:

```
docker run --rm -p 8080:8080 --name reducer --net project-net -v $(pwd)/volumes:/usr/src/app/volumes -t project_reducer
```

9) Send post request with subsample of audiofile to 127.0.0.1:8080, for example using curl: 

```curl -X POST --data-binary @requests/Again.m4a 127.0.0.1:8080/```

where `requests/Again.m4a` relative path to file

10) Stop containers

```
docker container stop server1
docker container stop server2
docker container stop reducer
```

## Structure of repository

`docker` - dir with data for run server

`indexing` - jupyter notebook for creating index and compute metrics (statistics)

`requests` - subsample of audios (all of them was recorded with mic, except `Arkansas_Traveler_noise.wav` what was created with adding gausian noise )

`names` - mapping among name of index and which audio-index it contain. To download audios you can use https://www.youtube.com/audiolibrary/music?nv=1 (please remember that when searching for audio, replace '_' with ' ' and remove '.mp3'), all audios was collected from this link.

## Statistics

1450 audio files were indexed from https://www.youtube.com/audiolibrary/music?nv=1 . 
An experiment was conducted to evaluate the accuracy of the algorithm, in which each audio file was searched for, and a 30-second sample was selected from each audio file with the addition of Gaussian noise (with std=0.1). The results are shown below:
```
Top1 0.991428
Top5 0.993571
```
