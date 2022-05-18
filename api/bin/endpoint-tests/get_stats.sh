#!/bin/sh

curl -X GET -H 'Content-Type: application/json' localhost:9999/stats/ -d "{\"user_id\": \"$1\"}" | jq
