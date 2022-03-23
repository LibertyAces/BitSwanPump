Deployment Overview
===================


- clone gitlab repository to /opt folder

- add 127.0.0.1 bs01 to /etc/hosts.conf

- check if disks on server are hdd or sdd using command

``cat /sys/block/sda/queue/rotational``

for single disk

or

``lsblk -d -o name, rota``

for mor disks, but you have to install it using

``sudo apt install util-linux``

check what disks to use and mount them if needed to create data

rewrite the in the config accordingly

change all disks to hdd/sdd in docker-compose.yaml

try running docker compose up





ERRORS and how to fix it
========================

- docker compose version is unsupported

        check the version of docker compose if needed upgrade it

- from daemon head url image:  no basic auth credential

    ask Robin for auth