SUDO=sudo

## Build base image and tag as quay.io/riotkit/boautomate-executor-base-img
build_base_image:
	${SUDO} docker build . -f ./docker/base-image/Dockerfile -t quay.io/riotkit/boautomate-executor-base-img
