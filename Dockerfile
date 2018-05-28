FROM asab:latest
MAINTAINER TeskaLabs Ltd (support@teskalabs.com)

RUN set -ex \
	&& apk update \
    && apk upgrade \
	&& apk add git

RUN set -ex \
	&& pip install git+https://github.com/TeskaLabs/bspump

CMD ["python3", "-m", "asab"]
