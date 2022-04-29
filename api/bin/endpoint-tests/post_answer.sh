#!/bin/sh

curl -X POST -H 'Content-Type: application/json' localhost:9999/answers/ -d "{\"word\": \"$1\"}" | jq
