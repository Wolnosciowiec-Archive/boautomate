
#.SILENT:

URL=http://localhost:8080
TEST_PIPE=/pipeline/test-pipeline\?secret\=test

test_quay_push_event:
	cat payload-examples/quay-push-event.json
	curl -X POST -f -s ${URL}${TEST_PIPE} --data @payload-examples/quay-push-event.json
