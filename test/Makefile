
.SILENT:

URL=http://localhost:8080
TEST_PIPE=/pipeline/22608b1b-f114-4f7a-b882-f6ed788a87b9\?secret\=test

test_quay_push_event:
	cat payload-examples/quay-push-event.json
	curl -X POST -f -s ${URL}${TEST_PIPE} --data @payload-examples/quay-push-event.json
