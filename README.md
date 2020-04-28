# IR project (shazam)

## How to run

1) Download index from https://drive.google.com/open?id=1mUER-xSxItbWKEfywzuRUDZa8LFZt0qN
2) Create dir for indexes: `mkdir docker/volumes -p`
2) Put index files into docker/volumes (you need to put at least one index file)
3) Build docker container 

```docker build docker/ -t ir_project```

4) Run container 

```docker run --rm -p 8080:8080 -v $(pwd)/docker/volumes/:/usr/src/app/volumes ir_project```

5) Send post request with subsample of audiofile to 127.0.0.1:8080, for example using curl: 

```curl -X POST --data-binary @requests/Again.m4a 127.0.0.1:8080/```

where `requests/Again.m4a` relative path to file

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
