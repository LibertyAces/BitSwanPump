# Installation #

    lxc launch images:alpine/3.8 pyarrow
    lxc exec pyarrow  -- /bin/ash

    apk add python3
    apk add boost
    apk add py3-numpy

    pip3 install six

    wget pyarrow_0_11_0-36m-x86_64-alpine38.tar.gz
    tar xzvf pyarrow_0_11_0-36m-x86_64-alpine38.tar.gz -C /usr/lib/python3.6/site-packages/
    rm pyarrow_0_11_0-36m-x86_64-alpine38.tar.gz

# Build

The process of the pyarrow build is described in build.md
