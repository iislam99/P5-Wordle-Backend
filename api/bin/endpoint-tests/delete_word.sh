#!/bin/sh

curl -X DELETE -H 'Content-Type: application/json' localhost:9999/words/ -d "{\"word\": \"$1\"}" | jq
