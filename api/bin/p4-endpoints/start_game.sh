#!/bin/sh

curl -X PUT -H 'Content-Type: application/json' localhost:9999/start/ -d "{\"username\": \"$1\"}"  | jq
