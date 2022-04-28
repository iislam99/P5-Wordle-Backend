#!/bin/sh

curl -X POST -H 'Content-Type: application/json' localhost:5200/finish/ -d "{\"username\": \"$1\", \"game_id\": \"$2\", \"guesses\": \"$3\", \"won\": \"$4\"}" | json_pp