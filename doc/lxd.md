# Deploying BSPump into a LXD container

	CONTAINER_NAME=bspump1
	lxc launch images:alpine/edge ${CONTAINER_NAME}
	lxc exec bspump1 -- apk update
	lxc exec bspump1 -- apk upgrade
	lxc exec bspump1 -- apk add --no-cache python3
	lxc exec bspump1 -- python3 -m ensurepip
	lxc exec bspump1 -- pip3 install asab
	lxc exec bspump1 -- rm -rf /var/cache/apk/*
	lxc exec bspump1 -- /opt/bspump/bspump.py

	vi /etc/init.d/bspump
	#!/sbin/openrc-run

	command="/opt/bspump/bspump.py"
	command_background="yes"
	pidfile="/run/$RC_SVCNAME.pid"

	:wq

	chmod a+x /etc/init.d/bspump
	rc-update add bspump

	lxc exec bspump1 -- reboot


_TODO:_ pypy version.

