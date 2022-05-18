#!/bin/sh

curl -X PUT -H 'Content-Type: application/json' localhost:9999/make_guess/ -d "{\"user_id\": \"$1\", \"game_id\": \"$2\", \"guess\": \"$3\"}"  | jq
