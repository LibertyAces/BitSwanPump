About
=====

This tutorial will help you to create your own Docker image for your pipeline. First things first, I would recommend you to go through
`Docker Documentation<https://docs.docker.com/get-started/>`_ if this is your first time with Docker.



quickstart to docker
--------------------

Docker can help you with deployment of your app on other devices. Everything you need to do is to setup docker one device
and then it works on every other device. Firstly you have to create docker image for you application. In our case we will create
image for our BS Pipeline. To do that we have to firstly create a docker file for our pipeline.

We will be using code for our TODO LINK


docker file
-----------

Docker file

::

    FROM  teskalabs/bspump:nightly

    WORKDIR /opt/nameofworkdir

    COPY name.py ./name.py


    CMD ["python3", "name.py"]


commands
--------


docker build

docker tag

docker push

docker ps

docker ps -a

docker run __name__




what next
---------

if you have sucessfully created your own docker image you can try to connected your pipeline with other componenst like elastic search
or kafka. Check our `tutorial <>` for working with docker compose

..
