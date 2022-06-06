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

create /data/hdd folder and mount it on desired disk partition
mount /var/lib/docker folder on desired disk partition
add mounted folders to /etc/fstab

rewrite the in the config accordingly

change all disks to hdd/sdd in docker-compose.yaml

try running docker compose up


setup password in ElasticSearch docker exec -it bs01-es01 bash

and run command ./bin/elasticsearch-setup-passwords interactive

set up: [password]



to deploy SeaCatAuth you need to generate domain from customer

then generate certifications, private key and CA

add mongoDB to docker compose

add seacatauth to docker compose

ask costumer if they have SMTP server for SeaCat email sender if then haven't generate api key from TeskaLabs Sendgrid
add provisioning mode to SeacatAuth into docker-compose via this docs https://docs.teskalabs.com/seacat-auth/config/provisioning


add BitSwan UI, Seacat WebUI and Seacat Auth WebUI to /data/hdd/nginx/webroot folder (UIs is on the GitLab)

after UI is ready to use create new superuser in Seacat and disable provisioning mode in docker-compose

to run kibana create global role elk:superuser

to run grafana create global role grafana:grafana_admin

to connect dashboards, sidebar and discover you have to create nodes in zookeper-ui

BSQuery
add service to docker compose
add node to zookeeper-ui /export
implement config
add endpoint to nginx config

ERRORS and how to fix it
========================

- docker compose version is unsupported

        check the version of docker compose if needed upgrade it

- from daemon head url image:  no basic auth credential

    ask Robin for auth

- elastic search ElasticsearchException[failed to bind service]; nested: AccessDeniedException[/usr/share/elasticsearch/data/nodes]

use chown -R elasticsearch data/ inside the container

- make sure that grafana.db is not a folder but a file, if it is folder delete it and restart grafana