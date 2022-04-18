# Wordle Clone

### Created by
* Aaron Lieberman
* Armanul Ambia
* Iftekharul Islam
* Jacob Nguyen

## Installation

1. Clone the directory
```bash
git clone https://github.com/AaronLieb/WordleClone.git
```

2. Enter the repository directory
```bash
cd WordleClone
```

3. Install the required libraries and tools
```bash
sudo apt update
sudo apt install --yes python3-pip ruby-foreman sqlite3 httpie jq
python3 -m pip install 'fastapi[all]' sqlite-utils
```

4. Go into the `api` directory
```bash
cd api
```

5. Run the initialization script
```bash
./bin/init.sh
```
This will download the wordle wordlists, parse them, create the database, and fill the database

6. Start both microservices
```bash
foreman start
```

7. To view the documentation of the endpoints, open the swagger docs

On the port for the microservice use the `/docs/` endpoint to check the available endpoints for that microservice

8. In a separate terminal, you can test the microservices using the scripts in the `bin/endpoint-tests/` directory
Most of the scripts use command line arguments to send words, here is an example of one being used

Test word validation:
```bash
./bin/endpoint-tests/put_validate.sh <word>
```

9. Project 3 end points

Test posting win or loss:
```bash
./bin/endpoint-tests/post_win_loss.sh <user_id> <game_id> <guesses> <won>
```
In this script, 5 argument parameters are passed in, user_id: int, game_id: int, guesses: int, and won: bool (1 or 0)

Test getting stats:
```bash
./bin/endpoint-tests/get_stats.sh <user_name> <user_id> 
```
If the user_id is not known we can also use
```bash
./bin/endpoint-tests/get_stats.sh <user_name>
```

Test Getting Users with Most Wins:
```bash
./bin/endpoint-tests/get_top_wins.sh
```

Test Getting Users with Longest Streak:
```bash
./bin/endpoint-tests/get_longest_streak.sh
```
