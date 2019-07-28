SUDO=sudo

## Build base image and tag as quay.io/riotkit/boautomate-executor-base-img
build_base_image:
	${SUDO} docker build . -f ./docker/base-image/Dockerfile -t quay.io/riotkit/boautomate-executor-base-img

## Run test instance for API testing
run_test:
	touch db.sqlite3
	${SUDO} python3 ./boautomate/__init__.py --db-string=sqlite:///db.sqlite3 --storage "@example(file://$$(pwd)/test/example-installation)" --log-level=debug --log-path=boautomate-test.log
