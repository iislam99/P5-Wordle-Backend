#!/bin/sh

sqlite3 ./var/valid_words.db < ./share/valid_words.sql
sqlite3 ./var/answers.db < ./share/answers.sql

sqlite-utils insert ./var/valid_words.db ValidWords ./share/dict/words/valid_words.csv --csv --detect-types
sqlite-utils insert ./var/answers.db Answers ./share/dict/words/answers.csv --csv
