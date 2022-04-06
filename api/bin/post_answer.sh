#!/bin/sh

curl -X POST -H 'Content-Type: application/json' localhost:5100/answer/ -d "{\"word\": \"$1\"}"
