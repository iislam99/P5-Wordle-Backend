#!/bin/sh

curl -X PUT -H 'Content-Type: application/json' localhost:9999/start/ -d "{\"og_id\": \"$1\", \"game_id\": \"$2\"}"  | jq
