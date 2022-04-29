#!/bin/sh

curl -X DELETE -H 'Content-Type: application/json' localhost:9999/next-answer/ | jq
