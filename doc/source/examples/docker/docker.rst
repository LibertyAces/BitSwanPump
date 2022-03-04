Docker File Quickstart
======================


About
=====

This tutorial will help you to create your own Docker image for your pipeline. First things first, I would recommend you to go through
`Docker Documentation<https://docs.docker.com/get-started/>`_ if this is your first time with Docker.


quickstart to docker
--------------------

Docker can help you with deployment of your app on other devices. Everything you need to do is to setup docker one device
and then it works on every other device. Firstly you have to create docker image for you application. In our case we will create
image for our BS Pipeline. To do that we have to firstly create a docker file for our pipeline.

We will be using code from one of our examples :ref:`coindesk`. You can simply copy paste the code and everything should be working
if you have a bspump python module installed

docker file
-----------

Creating a docker file is very easy thing to do. You have only copy-paste the code below

::

    FROM  teskalabs/bspump:nightly

    WORKDIR /opt/coindesk

    COPY coindesk.py ./coindesk.py

    CMD ["python3", "coindesk.py"]

To explain what is does:


1. keyword ``FROM`` specifies what docker image you are using. In this case we will be using a "preset" for a bspump.
This image is running on Alpine linux and has all libraries installed.

2. ``WORKDIR`` specifies the name of your working directory to where other files will be copied

3. ``COPY`` this command is used to copy any files you will be using including the source code of your app.

4. ``CMD`` is a command for running commands in your container. You have to write a command sequence as a list where
each element is one word of the command. In our case we want to execute our program using ``python3 coindesk.py``


Creating docker image
---------------------

The only thing you ashve

::

    docker build -t <<your docker nickname>>/<<name of your image>> .

Now you can try to run your docker image using:

::

    docker run -it <<your docker nickname>>/<<name of your image>>

now your container should be running in your console. If you want to terminate it open another console and type

::

    docker ps

This command will show you all your running containers and with

::

    docker kill <<CONTAINER ID>>

It will terminate the container. Container ID should be found next to the running image after typing ``docker ps``

If you want to see all containers that were initiated type

::

    docker ps -a






additional commands
-------------------



what next
---------

if you have sucessfully created your own docker image you can try to connected your pipeline with other componenst like elastic search
or kafka. Check our `tutorial <>` for working with docker compose

..
