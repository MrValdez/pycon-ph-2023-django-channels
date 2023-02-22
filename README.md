# pycon-ph-2022-django-channels


## Fundamental Git and Django knowledge needed

Before the workshop starts, please familiarize yourself with Django. I would recommend following the excellent Django tutorial (https://docs.djangoproject.com/en/4.1/intro/tutorial01/) to get you started. 


## Clone the workshop's git

$ git clone https://github.com/MrValdez/pycon-ph-2022-django-channels.git  
$ git checkout 001-initial-django


## Software requirements

This workshop requires at least Python 3.7, Django 3.2, Channels 4.0, Channels Daphne, Channels_redis, and redis. Higher versions of these requirements are allowed.

You can install the above via the following command line:

$ pip install -U -r requirements.txt

You can install redis either via docker or bare metal. To install with docker, use the following command:

$ docker run -d --name redis -p 6379:6379 -p 8001:8001 redis:latest

Alternatively, you can install directly to your OS. Instructions can be found on this link: https://redis.io/docs/getting-started/installation/

Running redis natively can be done with this command line:

$ sudo service redis-server start


## Check that Redis is working
To check if Redis have been installed correctly, you can run redis-cli and send a ping command.

$ redis-cli

For docker, you can use the following command 

$ docker exec -it redis redis-cli

A sample of Redis' ping output:

127.0.0.1:6379> ping
PONG


## Run Celery

$ celery -A pycon2023 worker -l INFO  
$ celery -A pycon2023 beat -l INFO

(note: under windows, add -P solo)


## Stock images used

Rock paper scissors image taken from: https://www.shutterstock.com/image-vector/rock-paper-scissors-icon-set-vector-1804156864  
Loading gif image taken from: https://icon-library.com/icon/loading-icon-animated-gif-19.html  
Loading static image taken from: https://www.vectorstock.com/royalty-free-vector/loading-icon-load-load-icon-white-background-vector-26979388