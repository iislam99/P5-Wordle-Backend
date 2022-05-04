#!/bin/sh

echo "Running init...."
# Create the var folder that will store the db files
mkdir var 2> /dev/null

# Create a variable for the answers file
answers='share/dict/answers.csv'

# Add the id and word header to the columns
echo "id,word" > $answers

echo "Downloading word lists..."
# Download the wordle script, parse the words, append to answers
curl --silent https://www.nytimes.com/games/wordle/main.bfba912f.js |
sed -e 's/^.*var Ma=//' -e 's/,Oa=.*$//' -e 1q | jq | tail -n +2 | head -n -1 | cut -c4-8 | awk '{print NR-1","$0}' >> $answers 

# Create a variable for the valid words file
valid_words='share/dict/words.csv'

# Add the word header to the column
echo "word" > $valid_words

# Download all valid wordle words, append to valid_words
curl --silent https://gist.githubusercontent.com/dracos/dd0668f281e685bad51479e5acaadb93/raw/ca9018b32e963292473841fb55fd5a62176769b5/valid-wordle-words.txt >> $valid_words

echo "Initialize databases..."
# Initialize the schema for the databases
sqlite3 ./var/valid_words.db < ./share/valid_words.sql
sqlite3 ./var/answers.db < ./share/answers.sql
# this populated sql file will also read in values for stats.db
sqlite3 ./var/stats.db < ./share/sqlite3-populated.sql

# Initialize sharded databases for games and users
sqlite3 ./var/games_1.db < ./share/games.sql
sqlite3 ./var/games_2.db < ./share/games.sql
sqlite3 ./var/games_3.db < ./share/games.sql
sqlite3 ./var/users.db < ./share/users.sql
./sharding.py

# Add view data to Redis db
./views_data.py

echo "Insert data into databases..."
# Insert the data from the word csv files into the databases
sqlite-utils insert ./var/valid_words.db ValidWords ./share/dict/words.csv --csv --detect-types
sqlite-utils insert ./var/answers.db Answers ./share/dict/answers.csv --csv

echo "Downloading traefik binary..."
mkdir temp
curl --silent -L -o traefik.tar.gz https://github.com/traefik/traefik/releases/download/v2.6.3/traefik_v2.6.3_linux_amd64.tar.gz
tar -xf traefik.tar.gz -C temp 2>&1 1>/dev/null
mv ./temp/traefik . 
rm -rf temp
rm traefik.tar.gz

echo "All done :)"
