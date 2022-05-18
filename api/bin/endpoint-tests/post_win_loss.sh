#!/bin/sh

curl -X POST -H 'Content-Type: application/json' localhost:9999/finish/ -d "{\"user_id\": \"$1\", \"game_id\": \"$2\", \"guesses\": \"$3\", \"won\": \"$4\"}" | jq
