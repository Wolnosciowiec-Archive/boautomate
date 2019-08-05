SUDO=sudo
SHELL=/bin/bash
.SILENT:
.PHONY: help

help:
	@grep -E '^[a-zA-Z\-\_0-9\.@]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build_base_image: ## Build base image and tag as quay.io/riotkit/boautomate-executor-base-img
	${SUDO} docker build . -f ./docker/base-image/Dockerfile -t quay.io/riotkit/boautomate-executor-base-img

run_test_server: ## Run test instance for API testing
	touch db.sqlite3
	${SUDO} python3 ./boautomate/__init__.py --db-string=sqlite:///db.sqlite3 --node-master-url=http://$$(ip route| grep $$(ip route |grep default | awk '{ print $$5 }') | grep -v "default" | awk '/scope/ { print $$9 }'):8080 --http-port=8080 --local-path=./test/example-installation/boautomate-local --log-level=debug --log-path=boautomate-test.log

@test_locks_example: ## Locks example pipeline
	bash -c "time curl -q -X POST http://localhost:8080/pipeline/locks-example/execute\?secret\=test -vvv"

@test_params: ## Parameters example pipeline
	bash -c "time curl -q -X POST http://localhost:8080/pipeline/params-example/execute\?secret\=test -vvv"

@test_params_with_query_string: ## Parameters example pipeline (with message=Unite.)
	bash -c "time curl -q -X POST -H 'Message: This is from header' http://localhost:8080/pipeline/params-example/execute\?secret\=test\&message\=Unite. -vvv"
