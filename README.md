# Wordle Clone

run the init script from /bin/init.sh

downloaded the answers.json
downloaded all valid wordle words from some github gist
cat answers.json | jq | cut -c4-8 > answers.csv

add the column name header "word" to each csv file

python3 -m pip install sqlite-utils
