FROM asab:latest
MAINTAINER TeskaLabs Ltd (support@teskalabs.com)

RUN set -ex \
	&& apk update \
    && apk upgrade \
	&& apk add git

RUN set -ex \
	&& pip install aiohttp \
	&& pip install git+https://github.com/TeskaLabs/bspump

EXPOSE 80/tcp

CMD ["python3", "-m", "bspump", "-w"]
