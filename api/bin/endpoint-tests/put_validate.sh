#!/bin/sh

curl -X PUT -H 'Content-Type: application/json' localhost:9999/validate/ -d "{\"word\": \"$1\"}" | jq
